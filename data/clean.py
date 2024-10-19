data = []

with open('./user-agents.txt', 'r') as f:
    for i in f:
        item = i.rstrip()
        if "Windows" in item and "compatible" not in item:
            data.append(item)

with open('new-agent.txt', 'w') as f:
    for i in data:
        f.write(i+'\n')