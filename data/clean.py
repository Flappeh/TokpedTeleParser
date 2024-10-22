
data = []

with open('./user-agents.txt','r') as f:
    for i in f:
        data.append(i.rstrip('\n'))

with open('./user-agents-new.txt', 'w') as f:
    for i in data:
        if "Mozilla/5.0 (Windows NT 6.3; Win64; x64;" in i:
            f.write(i+'\n')