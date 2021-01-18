#!/bin/bash
i=0
for WOOF in {0,1}; do
        for SIZE in {128,192,256}; do
            for EPOCHS in {5,20,80,200}; do
                i=$((i+1))
                echo $i
                echo $WOOF $PCT_NOISE $SIZE $EPOCHS
                python train_noisy_imagenette.py --woof $WOOF --pct_noise $1 --size $SIZE --epochs $EPOCHS --lr 8e-3 --sqrmom 0.99 --mom 0.95 --eps 1e-6 --bs 64 --opt ranger --sa --fp16 --arch xse_resnext50 --pool MaxPool --gpu $2 --repro
            done
        done
done