from fastai.basics import *
from fastai.vision.all import *
from fastai.callback.all import *
from fastai.distributed import *
from fastprogress import fastprogress
from torchvision.models import *
from fastai.vision.models.xresnet import *
from fastai.callback.mixup import *
from fastcore.script import *


torch.backends.cudnn.benchmark = True
fastprogress.MAX_COLS = 80

def get_dls(size, woof, pct_noise, bs, sh=0., workers=None):
    if size<=224: path = URLs.IMAGEWOOF_320 if woof else URLs.IMAGENETTE_320
    else        : path = URLs.IMAGEWOOF     if woof else URLs.IMAGENETTE
    source = untar_data(path)
    if workers is None: workers = min(8, num_cpus())
    csv_file = 'noisy_imagewoof.csv' if woof else 'noisy_imagenette.csv'
    df = pd.read_csv(csv_file)
    batch_tfms = [Normalize.from_stats(*imagenet_stats)]
    if sh: batch_tfms.append(RandomErasing(p=0.3, max_count=3, sh=sh))
    dblock = DataBlock(blocks=(ImageBlock, CategoryBlock),
                       splitter=ColSplitter(),
                       get_x=ColReader('path', pref=source), 
                       get_y=ColReader(f'noisy_labels_{pct_noise}'),
                       item_tfms=[RandomResizedCrop(size, min_scale=0.35), FlipItem(0.5)],
                       batch_tfms=batch_tfms)
    return dblock.dataloaders(df, bs=bs, num_workers=workers)


@call_parse
def main(
    woof:     Param("Use imagewoof (otherwise imagenette)", int)=0,
    pct_noise:Param("Percentage of noise in training set (1,5,25,50%)", int)=25,
    lr:       Param("Learning rate", float)=1e-2,
    size:     Param("Size (px: 128,192,256)", int)=128,
    sqrmom:   Param("sqr_mom", float)=0.99,
    mom:      Param("Momentum", float)=0.9,
    eps:      Param("epsilon", float)=1e-6,
    epochs:   Param("Number of epochs", int)=5,
    bs:       Param("Batch size", int)=64,
    mixup:    Param("Mixup", float)=0.,
    opt:      Param("Optimizer (adam,rms,sgd,ranger)", str)='ranger',
    arch:     Param("Architecture", str)='xresnet50',
    sh:       Param("Random erase max proportion", float)=0.,
    sa:       Param("Self-attention", store_true)=False,
    sym:      Param("Symmetry for self-attention", int)=0,
    beta:     Param("SAdam softplus beta", float)=0.,
    act_fn:   Param("Activation function", str)='Mish',
    fp16:     Param("Use mixed precision training", store_true)=False,
    pool:     Param("Pooling method", str)='AvgPool',
    dump:     Param("Print model; don't train", int)=0,
    runs:     Param("Number of times to repeat training", int)=1,
    gpu:      Param("Specify GPU", int)=0,
    repro:    Param("Reproducible run", store_true)=False,
    meta:     Param("Metadata (ignored)", str)=''
):

    "Training of Noisy Imagenette. Call with `python -m fastai.launch` for distributed training"
    
    if repro: set_seed(42, reproducible=True)
    torch.cuda.set_device(gpu); print(f'GPU {gpu} is used')

    if   opt=='adam'  : opt_func = partial(Adam, mom=mom, sqr_mom=sqrmom, eps=eps)
    elif opt=='rms'   : opt_func = partial(RMSprop, sqr_mom=sqrmom)
    elif opt=='sgd'   : opt_func = partial(SGD, mom=mom)
    elif opt=='ranger': opt_func = partial(ranger, mom=mom, sqr_mom=sqrmom, eps=eps, beta=beta)

    dls = get_dls(size, woof, pct_noise, bs, sh)
    
    print(f'pct_noise: {pct_noise}; epochs: {epochs}; lr: {lr}; size: {size}; sqrmom: {sqrmom}; mom: {mom}; eps: {eps}')
    m,act_fn,pool = [globals()[o] for o in (arch,act_fn,pool)]

    for run in range(runs):
        print(f'Run: {run}')
        learn = Learner(dls, m(n_out=10, act_cls=act_fn, sa=sa, sym=sym, pool=pool), opt_func=opt_func, \
                metrics=[accuracy,top_k_accuracy], loss_func=LabelSmoothingCrossEntropy())
        if dump: pr(learn.model); exit()
        if fp16: learn = learn.to_fp16()
        cbs = MixUp(mixup) if mixup else []
        learn.fit_flat_cos(epochs, lr, wd=1e-2, cbs=cbs)
