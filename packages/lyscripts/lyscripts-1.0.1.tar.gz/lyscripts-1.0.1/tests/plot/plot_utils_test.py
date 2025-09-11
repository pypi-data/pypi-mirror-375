"""Testing of the utilities implemented for the plotting routines."""

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.testing.compare as mpl_comp
import numpy as np
import pytest

from lyscripts.plots import (
    BetaPosterior,
    Histogram,
    ceil_to_step,
    draw,
    floor_to_step,
    get_size,
    save_figure,
)


@pytest.fixture
def beta_samples() -> str:
    """Name of HDF5 file where some samples from a Beta distribution are stored."""
    return "./tests/plot/data/beta_samples.hdf5"


def test_floor_to_step():
    """Check correct rounding down to a given step size."""
    numbers = np.array([0.0, 3.0, 7.4, 2.01, np.pi, 12.7, 12.7, 17.3])
    steps = np.array([2, 2, 5, 2, 3, 3, 5, 0.17])
    exp_res = np.array([0.0, 2.0, 5.0, 2.0, 3.0, 12.0, 10.0, 17.17])

    comp_res = np.zeros_like(exp_res)
    for i, (num, step) in enumerate(zip(numbers, steps, strict=False)):
        comp_res[i] = floor_to_step(num, step)

    assert all(np.isclose(comp_res, exp_res)), "Floor to step did not work properly."


def test_ceil_to_step():
    """Check correct rounding up to a given step size."""
    numbers = np.array([0.0, 3.0, 7.4, 2.01, np.pi, 12.7, 12.7, 17.3])
    steps = np.array([2, 2, 5, 2, 3, 3, 5, 0.17])
    exp_res = np.array([2.0, 4.0, 10.0, 4.0, 6.0, 15.0, 15.0, 17.34])

    comp_res = np.zeros_like(exp_res)
    for i, (num, step) in enumerate(zip(numbers, steps, strict=False)):
        comp_res[i] = ceil_to_step(num, step)

    assert all(np.isclose(comp_res, exp_res)), "Ceil to step did not work properly."


def test_histogram_cls(beta_samples: str):
    """Make sure the histogram data container works as intended."""
    str_filename = beta_samples
    path_filename = Path(str_filename)
    non_existent_filename = "non_existent.hdf5"
    custom_label = "Lorem ipsum"

    hist_from_str = Histogram.from_hdf5(filename=str_filename, dataname="beta")
    hist_from_path = Histogram.from_hdf5(
        filename=path_filename,
        dataname="beta",
        scale=10.0,
        label=custom_label,
    )

    with pytest.raises(FileNotFoundError):
        Histogram.from_hdf5(filename=non_existent_filename, dataname="does_not_matter")

    assert np.all(
        np.isclose(hist_from_str.values, 10.0 * hist_from_path.values)
    ), "Scaling of data does not work correclty"
    assert np.all(
        np.isclose(
            hist_from_str.left_percentile(50.0),
            hist_from_str.right_percentile(50.0),
        )
    ), "50% percentiles should be the same from the left and from the right."
    assert np.all(
        np.isclose(
            hist_from_path.left_percentile(10.0),
            hist_from_path.right_percentile(90.0),
        )
    ), "10% from the left is not the same as 90% from the right"
    assert (
        hist_from_str.kwargs["label"] == "beta | mega scan | 100 | ext"
    ), "Label extraction did not work"
    assert (
        hist_from_path.kwargs["label"] == custom_label
    ), "Keyword override did not work"


def test_inverted_histogram_cls(beta_samples: str):
    """Make sure the histogram data container works as intended."""
    str_filename = beta_samples
    path_filename = Path(str_filename)
    custom_label = "Lorem ipsum"

    hist_from_str = Histogram.from_hdf5(filename=str_filename, dataname="beta")
    hist_from_path = Histogram.from_hdf5(
        filename=path_filename,
        dataname="beta",
        scale=-100.0,
        offset=100.0,
        label=custom_label,
    )

    assert np.all(
        np.isclose(100.0 - hist_from_str.values, hist_from_path.values)
    ), "Scaling and offsetting of data does not work correclty"
    assert np.all(
        np.isclose(
            hist_from_str.left_percentile(50.0),
            hist_from_str.right_percentile(50.0),
        )
    ), "50% percentiles should be the same from the left and from the right."
    assert np.all(
        np.isclose(
            hist_from_path.left_percentile(10.0),
            hist_from_path.right_percentile(90.0),
        )
    ), "10% from the left is not the same as 90% from the right"
    assert (
        hist_from_str.kwargs["label"] == "beta | mega scan | 100 | ext"
    ), "Label extraction did not work"
    assert (
        hist_from_path.kwargs["label"] == custom_label
    ), "Keyword override did not work"


def test_posterior_cls(beta_samples: str):
    """Test the container class for Beta posteriors."""
    str_filename = beta_samples
    path_filename = Path(str_filename)
    non_existent_filename = "non_existent.hdf5"
    custom_label = "Lorem ipsum"
    x_10 = np.linspace(0.0, 10.0, 100)
    x_100 = np.linspace(0.0, 100.0, 100)

    post_from_str = BetaPosterior.from_hdf5(filename=str_filename, dataname="beta")
    post_from_path = BetaPosterior.from_hdf5(
        filename=path_filename,
        dataname="beta",
        scale=10.0,
        label=custom_label,
    )

    with pytest.raises(FileNotFoundError):
        BetaPosterior.from_hdf5(
            filename=non_existent_filename, dataname="does_not_matter"
        )

    assert (
        post_from_str.num_success == post_from_path.num_success == 20
    ), "Number of successes not correctly extracted"
    assert (
        post_from_str.num_total == post_from_path.num_total == 40
    ), "Total number of trials not correctly extracted"
    assert (
        post_from_str.num_fail == post_from_path.num_fail == 20
    ), "Number of failures not correctly computed"
    assert np.all(
        np.isclose(
            10 * post_from_str.pdf(x_100),
            post_from_path.pdf(x_10),
        )
    ), "PDFs with different scaling do not match"
    assert np.all(
        np.isclose(
            post_from_str.left_percentile(50.0),
            post_from_str.right_percentile(50.0),
        )
    ), "50% percentiles should be the same from the left and from the right."
    assert np.all(
        np.isclose(
            post_from_path.left_percentile(10.0),
            post_from_path.right_percentile(90.0),
        )
    ), "10% from the left is not the same as 90% from the right"


@pytest.mark.mpl_image_compare
def test_draw(beta_samples: str):
    """Check the drawing function."""
    filename = Path(beta_samples)
    dataname = "beta"
    hist = Histogram.from_hdf5(filename, dataname)
    post = BetaPosterior.from_hdf5(filename, dataname)
    fig, ax = plt.subplots()
    ax = draw(axes=ax, contents=[hist, post], percent_lims=(2.0, 2.0))
    return fig


def test_draw_hist_kwargs(beta_samples: str):
    """Make sure the `hist_kwargs` can override the defaults."""
    filename = Path(beta_samples)
    dataname = "beta"

    hist = Histogram.from_hdf5(filename, dataname)
    default_kwargs_path = "./tests/plot/results/default_kwargs"
    fig, default_kwargs_ax = plt.subplots()
    default_kwargs_ax = draw(default_kwargs_ax, contents=[hist])
    save_figure(default_kwargs_path, fig, ["png"])

    bins_kwargs_path = "./tests/plot/results/bins_kwargs"
    fig, bins_kwargs_ax = plt.subplots()
    bins_kwargs_ax = draw(bins_kwargs_ax, contents=[hist], hist_kwargs={"bins": 70})
    save_figure(bins_kwargs_path, fig, ["png"])

    global_kwargs_path = "./tests/plot/results/global_kwargs"
    fig, global_kwargs_ax = plt.subplots()
    global_kwargs_ax = draw(
        global_kwargs_ax, contents=[hist], hist_kwargs={"alpha": 0.3}
    )
    save_figure(global_kwargs_path, fig, ["png"])

    hist = Histogram.from_hdf5(filename, dataname, alpha=0.3)
    local_kwargs_path = "./tests/plot/results/local_kwargs"
    fig, local_kwargs_ax = plt.subplots()
    local_kwargs_ax = draw(local_kwargs_ax, contents=[hist], hist_kwargs={"alpha": 1.0})
    save_figure(local_kwargs_path, fig, ["png"])

    assert (
        mpl_comp.compare_images(
            expected=default_kwargs_path + ".png",
            actual=bins_kwargs_path + ".png",
            tol=0.001,
        )
        is not None
    ), "Changing bin number did not result in different plot"

    assert (
        mpl_comp.compare_images(
            expected=default_kwargs_path + ".png",
            actual=global_kwargs_path + ".png",
            tol=0.001,
        )
        is not None
    ), "Changing global kwargs in `draw` did not result in different plot"

    assert (
        mpl_comp.compare_images(
            expected=local_kwargs_path + ".png",
            actual=global_kwargs_path + ".png",
            tol=0.001,
        )
        is None
    ), "Overriding global with `Histogram` specific kwargs did not work"


def test_save_figure(capsys):
    """Check that figures get stored correctly."""
    x = np.linspace(0.0, 2 * np.pi, 200)
    y = np.sin(x)
    fig, ax = plt.subplots(figsize=get_size())
    ax.plot(x, y)
    output_path = "./tests/plot/results/sine"
    formats = ["png", "svg"]

    save_figure(output_path, fig, formats)

    assert (
        mpl_comp.compare_images(
            expected="./tests/plot/baseline/sine.png",
            actual="./tests/plot/results/sine.png",
            tol=0.0,
        )
        is None
    ), "PNG of figure was not stored correctly."

    # Commented out, because I recently got the following message from matplotlib:
    # `SKIPPED (Don't know how to convert .svg files to png)`
    # So, I am commenting out this test for now.

    # assert mpl_comp.compare_images(
    #     expected="./tests/plot/baseline/sine.svg",
    #     actual="./tests/plot/results/sine.svg",
    #     tol=0.,
    # ) is None, "SVG of figure was not stored correctly."

    # assert save_figure_capture.out == expected_output, (
    #     "The output during the save figure procedure was wrong."
    # )
