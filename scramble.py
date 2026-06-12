## add dependecyes #TO DO
def group_by_base_var(data_var):
    '''gropus variant items by their base id (prefix before the first ":").
    -> {base_id: [list of variant items]}'''
    grouped_var_by_seed_id = defaultdict(list)
    for item in data_var:
      #print(item)
      grouped_var_by_seed_id[item['id'].split(':')[0]].append(item)
    return grouped_var_by_seed_id


def get_inventory_of_shared_words_p_h(dataset_file):
    '''load dataset, output an inventory of shared words between p and h per base id.
    -> {base_id: [shared_word_variant_1, shared_word_variant_2, ...]}'''
    with open(dataset_file, 'r') as f:
        dataset_data = json.load(f)

    grouped_by_seed = group_by_base_var(dataset_data)

    shared_words = {base_id: set([variant['id'].split(':')[1] for variant in variants])
        for base_id, variants in grouped_by_seed.items()
        }
    return shared_words


def shuffle_until_different(word, rng=random, max_tries=20):
    '''shuffle all word letter; 20 trys shuffled != original else return orginal (e.g. "aa").'''
    letters = list(word)
    for _ in range(max_tries):
        chars = letters[:]
        rng.shuffle(chars)
        if chars != letters:
            return ''.join(chars)
    return word


def apply_scrambling(word, scramble_type, rng=random):
    '''scrambles words. scramble word: '1'   -> last letter to the front (girl -> lgir)
    '2'   -> last two letters to the front (girl -> rlgi)
    'all' -> shuffle all letters'''
    if type(word) == list:
      #print(word[0])
      word=word[0]
    if scramble_type == '1':
        #print('word again', word)
        return word[-1] + word[:-1]

    if scramble_type == '2':
        return word[-2:] + word[:-2]

    if scramble_type == 'all':
        return shuffle_until_different(word, rng)

    raise ValueError(f"Unknown scramble_type: {scramble_type}")


def replace_original(premise, hypothesis, original, replacement):
    if type(original)==list:
      original=original[0]
    pattern = r'\b' + re.escape(original) + r'\b'
    return (re.sub(pattern, replacement, premise),
            re.sub(pattern, replacement, hypothesis))

def seed_scrambled(dataset_file, inventory, scramble_type):
    items, scrambled_words = [], defaultdict(list)
    with open(dataset_file, 'r') as f:
      dataset=json.load(f)
    for item in dataset:
        # print('the original word', inventory.get(item['id']))
        # print('type of the original word', type(inventory.get(item['id'])))
        if inventory.get(item['id'])==None:
          continue
        scrambled_word = apply_scrambling(inventory.get(item['id']), scramble_type)
        scrambled_words[item['id']] = scrambled_word
        premise_s, hypothesis_s = replace_original(item['premise'], item['hypothesis'], inventory.get(item['id']), scrambled_word)
        items.append({'id': item['id'],
                      'premise': premise_s,
                      'hypothesis': hypothesis_s,
                      'label': item['label']})
    return items, seed_scrambled

def save_json(dataset, name):
  '''[list of dictionaries of items]'''
  with open(name, 'w') as f:
    json.dump(dataset, f)
  print('new scrambled items saved as json file')

def transform_ivenotry(iventory, constrain_number):
  '''takes ivenotry of shared words and transform into list and keeps x amount of words'''
  if constrain_number is not None:
      return {base_id: list(values)[:constrain_number]
              for base_id, values in inventory.items()}
  return {base_id: list(values)
        for base_id, values in inventory.items()}

def scramble(dataset_file, dataset_type, inventory, scramble_type, constrain_number):
  '''scrmabled dataset
  if seed, it takes an inventory of shared words
  if variant, uses the id'''
  if dataset_type == 'seed':
      inventory= transform_ivenotry(inventory, constrain_number)
      return seed_scrambled(dataset_file, inventory, scramble_type)

def scrambled_word_present(item, list_scrambled, ivenotry_list):
  for word in list_scrambled:
    '''test scramble'''
    if word not in item['premise'] or word not in item['hypothesis']:
      print('SCRAMBLED WORD NOT PRESENT')
  for word in ivenotry_list:
    if word in item['premise'] or word in item['hypothesis']:
      print('ORIGINAL WORD PRESENT')
