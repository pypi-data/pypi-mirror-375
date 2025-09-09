from typing import Any, Callable, Generic, TypeVar, Iterator
from pydantic import BaseModel
from pandas import DataFrame

IT = TypeVar("IT")
T = TypeVar("T", bound=BaseModel)


class DataContainer(Generic[IT, T]):
    """
    Generic container for responses from the Impresso API
    returned by resource methods (`get`, `find`).

    Generally represents a single page of the result. The results can be
    paginated through by adjusting the `offset` and `limit` parameters
    in the corresponding resource method call (e.g., `client.newspapers.find`).
    The `total`, `limit`, `offset`, and `size` properties provide information
    about the current page and the overall result set.
    """

    def __init__(
        self,
        data: IT,
        pydantic_model: type[T],
        web_app_search_result_url: str | None = None,
    ):
        if data is None or getattr(data, "to_dict") is None:
            raise ValueError(f"Unexpected data object: {data}")
        self._data = data
        self._pydantic_model = pydantic_model
        self._web_app_search_result_url = web_app_search_result_url

    def _repr_html_(self):
        df_repr = self.df.head(3).to_html(notebook=True)
        response_type = self.__class__.__name__.replace("DataContainer", "").replace(
            "Container", ""
        )
        preview_img = self._get_preview_image_()

        grid_template_style = (
            "grid-template-columns: minmax(200px, 1fr) auto;"
            if preview_img is not None
            else ""
        )

        items = [
            f'<div style="display: grid; {grid_template_style}">',
            "<div>",
            f"<h2>{response_type} result</h2>",
            f"<div>Contains <b>{self.size}</b> items "
            + (
                f"(<b>{self.offset}</b> - <b>{self.offset + self.size}</b>) "
                if self.size > 0 and self.size < self.total
                else ""
            )
            + f"of <b>{self.total}</b> total items.</div>",
            "<br/>",
            (
                f'See this result in the <a href="{self.url}">Impresso App</a>.'
                if self.url
                else None
            ),
            "</div>",
            (
                (
                    f'<div style="align-content: center;"><img src="data:image/png;base64,{preview_img}" '
                    + 'style="max-width: 800px; width: 100%;"></div>'
                )
                if preview_img
                else None
            ),
            "</div>",
            "<h3>Data preview:</h3>",
            df_repr,
        ]

        return "\n".join([item for item in items if item])

    def _get_preview_image_(self) -> str | None:
        return None

    @property
    def raw(self) -> dict[str, Any]:
        """The response data as a python dictionary."""
        return getattr(self._data, "to_dict")()

    @property
    def pydantic(self) -> T:
        """The response data as a pydantic model."""
        return self._pydantic_model.model_validate(self.raw)

    @property
    def df(self) -> DataFrame:
        """
        The response data for the current page as a pandas dataframe.

        Note that this DataFrame only contains the items from the current
        page of results, not the entire result set across all pages.
        """
        return DataFrame.from_dict(self._data)  # type: ignore

    @property
    def total(self) -> int:
        """Total number of results available across all pages."""
        return self.raw.get("pagination", {}).get("total", 0)

    @property
    def limit(self) -> int:
        """Maximum number of items requested for the current page."""
        return self.raw.get("pagination", {}).get("limit", 0)

    @property
    def offset(self) -> int:
        """The starting index (0-based) of the items on the current page."""
        return self.raw.get("pagination", {}).get("offset", 0)

    @property
    def size(self) -> int:
        """Number of items actually present on the current page."""
        return len(self.raw.get("data", []))

    @property
    def url(self) -> str | None:
        """
        URL of an Impresso web application page representing the result set.
        """
        return self._web_app_search_result_url

    def pages(self) -> Iterator["DataContainer[IT, T]"]:
        """
        Yields the current page and all subsequent pages of results.

        This method first yields the current DataContainer instance (self),
        then attempts to fetch and yield subsequent pages by making new API
        calls with adjusted offsets.

        Returns:
            Iterator["DataContainer[IT, T]"]: An iterator that yields
            DataContainer instances, starting with the current one,
            followed by subsequent pages.

        Example:

            # Get the first page with 10 items per page
            first_page = client.newspapers.find(limit=10)

            # Iterate through all pages
            for page in first_page.pages():
                # Process items from the current page
                print(f"Page {page.offset // page.limit + 1}:")
                print(page.df)
                # The loop will continue with the next page, if any
        """
        # Implementation Note:
        # To fully implement this method, it should first `yield self`.
        # Then, it would need access to the original function/client method
        # that fetched the current page, along with its parameters, to make
        # new calls for subsequent pages in a loop, yielding each new
        # DataContainer. This might involve modifying the __init__
        # method to store this information. The loop would continue as long
        # as `self.offset + self.size < self.total`.

        # Default implementation is suitable for `Get*` containers that
        # contain 0 or 1 items and no further pages.
        yield self  # Return the current page
        raise StopIteration


DC = TypeVar("DC", bound=DataContainer)


def iterate_pages(
    fetch_method: Callable[..., DC],
    fetch_method_args: dict[str, Any],
    initial_offset: int,
    limit: int,
    total: int,
) -> Iterator[DC]:
    """
    Iterate over the pages of results from the media sources API, starting from the
    next page.

    Args:
        fetch_method (Callable[..., DC]): The method to call to fetch each page of results.
        fetch_method_args (dict[str, Any]): The arguments to pass to the fetch method.
        initial_offset (int): The initial offset for the first page.
        limit (int): The maximum number of items to fetch per page.

    Returns:
        Iterator[DC]: An iterator over the pages of results.
    """
    offset = initial_offset + limit
    while offset < total:
        page = fetch_method(
            **fetch_method_args,
            **{"offset": offset, "limit": limit},
        )
        yield page
        offset += limit
