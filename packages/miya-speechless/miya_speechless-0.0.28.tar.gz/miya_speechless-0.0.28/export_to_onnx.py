"""Export a pre-trained pyannote model to ONNX format."""

import click
import torch
import onnxruntime as ort

from pyannote.audio import Model

DUMMY_LENGTH = 160000


@click.command()
@click.argument("checkpoint", type=click.Path(exists=True, file_okay=True))
@click.argument("output", type=click.Path(exists=False, file_okay=True))
def main(checkpoint: str, output: str):
    """
    Export an onnx model from a pyannote checkpoint.

    Parameters
    ----------
    checkpoint : str
        The path to the pyannote checkpoint file.
    output : str
        The path to the output ONNX model file.
    """
    model = Model.from_pretrained(checkpoint)

    dummy_input = torch.zeros(3, 1, DUMMY_LENGTH)
    torch.onnx.export(
        model,
        dummy_input,
        output,
        do_constant_folding=True,
        input_names=["input"],
        output_names=["output"],
        dynamic_axes={
            "input": {0: "B", 1: "C", 2: "T"},
        },
    )
    opts = ort.SessionOptions()
    opts.log_severity_level = 3
    opts.optimized_model_filepath = output
    # so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    # ORT_DISABLE_ALL, ORT_ENABLE_BASIC, ORT_ENABLE_EXTENDED, ORT_ENABLE_ALL
    ort.InferenceSession(output, sess_options=opts)


if __name__ == "__main__":
    main()
