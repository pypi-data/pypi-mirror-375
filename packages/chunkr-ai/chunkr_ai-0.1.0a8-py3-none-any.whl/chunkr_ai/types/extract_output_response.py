# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["ExtractOutputResponse"]


class ExtractOutputResponse(BaseModel):
    citations: object
    """Mirror of `results`; leaves are `Vec<Citation>` for the corresponding field

    Example:

    ```json
    {
      "field_name": [
        {
          "citation_id": "abc1234",
          "citation_type": "Segment",
          "bboxes": [
            {
              "left": 10,
              "top": 20,
              "width": 100,
              "height": 18
            }
          ],
          "content": "Example content",
          "segment_id": "seg_001",
          "segment_type": "Text",
          "page_number": 1,
          "page_height": 297,
          "page_width": 210,
          "ss_ranges": ["A1:C10"],
          "ss_sheet_name": "Sheet1"
        }
      ]
    }
    ```
    """

    metrics: object
    """
    Mirror of `results`; leaves contain a `Metrics` object for the corresponding
    field

    Example:

    ```json
    { "field_name": { "confidence": "High" } }
    ```
    """

    results: object
    """JSON data that matches the provided schema

    Example:

    ```json
    { "field_name": "value" }
    ```
    """
