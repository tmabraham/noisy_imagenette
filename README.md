# Noisy Imagenette

This dataset is the same as fast.ai's [imagenette](https://github.com/fastai/imagenette), except the training labels are noisy. These labels are now provided in a CSV, with a column for labels with a desired noise level. There are 4 noise levels available: 1%, 5%, 25%, and 50% incorrect labels.

# Leaderboard

Generally you'll see +/- 1% differences from run to run since it's quite a small validation set. So please only send in contributions that are higher than the reported accuracy >80% of the time. Here's the rules:

* No inference time tricks, e.g. no: TTA, validation size > train size
* Must start with random weights
* Must be one of the size/#epoch combinations listed in the table
* If you have the resources to do so, try to get an average of 5 runs, to get a stable comparison. Use the "# Runs" column to include this (note that train_imagenette.py provides a --runs flag to make this easy)
* In the URL column include a link to a notebook, blog post, gist, or similar which explains what you did to get your result, and includes the code you used (or a link to it), including the exact commit, so that others can reproduce your result.

## Noisy Imagenette Leaderboard

WIP

## Noisy Imagewoof Leaderboard

WIP
