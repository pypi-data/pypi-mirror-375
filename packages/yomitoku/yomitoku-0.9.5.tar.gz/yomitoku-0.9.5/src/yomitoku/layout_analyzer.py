from .layout_parser import LayoutParser
from .table_structure_recognizer import TableStructureRecognizer

from .schemas import LayoutAnalyzerSchema


class LayoutAnalyzer:
    def __init__(self, configs={}, device="cuda", visualize=False):
        layout_parser_kwargs = {
            "device": device,
            "visualize": visualize,
        }
        table_structure_recognizer_kwargs = {
            "device": device,
            "visualize": visualize,
        }

        if isinstance(configs, dict):
            if "layout_parser" in configs:
                layout_parser_kwargs.update(configs["layout_parser"])

            if "table_structure_recognizer" in configs:
                table_structure_recognizer_kwargs.update(
                    configs["table_structure_recognizer"]
                )
        else:
            raise ValueError(
                "configs must be a dict. See the https://kotaro-kinoshita.github.io/yomitoku-dev/usage/"
            )

        self.layout_parser = LayoutParser(
            **layout_parser_kwargs,
        )
        self.table_structure_recognizer = TableStructureRecognizer(
            **table_structure_recognizer_kwargs,
        )

    def __call__(self, img):
        layout_results, vis = self.layout_parser(img)
        table_boxes = [table.box for table in layout_results.tables]
        table_results, vis = self.table_structure_recognizer(img, table_boxes, vis=vis)

        results = LayoutAnalyzerSchema(
            paragraphs=layout_results.paragraphs,
            tables=table_results,
            figures=layout_results.figures,
        )

        return results, vis
