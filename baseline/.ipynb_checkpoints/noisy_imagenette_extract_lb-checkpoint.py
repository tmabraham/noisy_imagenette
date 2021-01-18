import re
import pandas as pd

pct_noises = [1,5,25,50]
pct_noise = []
imagewoof = []
sizes = []
num_epochs = []
score = []

for pct_noise_level in pct_noises:
    f = open(f'noisy_imagenette_{pct_noise_level}.txt')
    i = 0
    previous_line = None
    current_line = f.readline()
    while current_line:
        current_line = f.readline()
        numbers = re.findall('\d+', current_line)
        if len(numbers)==3:
            imagewoof.append(numbers[0])
            sizes.append(numbers[1])
            num_epochs.append(numbers[2])
            pct_noise.append(pct_noise_level)
        if previous_line:
            if len(previous_line.split())==6 and len(numbers)==1:
                score.append(previous_line.split()[-3])
        i+=1
        previous_line = current_line
    f = open(f'noisy_imagenette_{pct_noise_level}.txt')
    previous_line = f.readlines()[-1]
    score.append(previous_line.split()[-3])
    
print(pct_noise)
print(imagewoof)
print(sizes)
print(num_epochs)
print(score)

print(len(pct_noise))
print(len(imagewoof))
print(len(sizes))
print(len(num_epochs))
print(len(score))

data_dict = {'pct_noise': pct_noise, 'imagewoof': imagewoof, 'size': sizes, 'epochs': num_epochs, 'accuracy': score}

df = pd.DataFrame(data_dict)
print(df)
df.to_csv('baseline_extended_lb.csv',index=False)