import  pickle
with open ('dicts/model_names_dict.pkl', 'rb') as f:
    entities = pickle.load(f)
def str2Entity(str):
    # uniform to upper case
    if entities.get(str.upper(), -1) != -1:
        return entities[str.upper()][0]
    else:
        return str

