import requests
from bs4 import BeautifulSoup
from .models import PortugueseVerb, Vocab
from .utils import *


def add_top_100_portuguese_verbs_to_vocabulary(user):
    verbs = download_top_100_portuguese_verbs()  # downloads 100 most frequent Portuguese verbs from website
    user_vocab = set(user.vocabulary.filter(language='pt').values_list('word_1', flat=True).distinct())
    verbs = [(verb, translation) for verb, translation in verbs if verb not in user_vocab]  # filter existing vocab
    new_vocab = [Vocab(user=user, language='pt', word_1=verb, word_2=translation) for verb, translation in verbs]
    Vocab.objects.bulk_create(new_vocab)  # new vocab
    PortugueseVerb.objects.bulk_create([PortugueseVerb(user=user, vocab=v) for v in new_vocab])  # new verbs


def download_top_100_portuguese_verbs():
    site = requests.get('https://languageposters.com/pages/portuguese-verbs')  # top 100 portuguese verbs
    soup = BeautifulSoup(site.content, 'lxml')

    def get_verb(x):
        return x.find('a').text.split()[0].lower()

    def get_translation(x):
        return x.find('span').text.replace('(', '').replace(')', '').lower()

    # Tuples (verb, translation) of the top 100 portuguese verbs
    return sorted([(get_verb(x), get_translation(x)) for x in soup.findAll('li')[71:171]])


def check_if_is_verb(vocab):
    url = f'https://conjpt.cactus2000.de/showverb.php?verb={vocab.word_1.replace("ü", "?")}'
    try:
        site = requests.get(url)
        soup = BeautifulSoup(site.content, 'lxml')
        table = soup.find('table', {'class': 'conjtab'})  # conjugation table
        cells = [cell.text for cell in table.findAll('td')]

        def get_tense(i):
            tense = cells[i].split(' / ')[0]
            return tense.replace('eu ', '').replace('ele ', '').replace('nós ', '').replace('eles ', '')

        new_values = {'present_eu': get_tense(2),
                      'present_ele': get_tense(6),
                      'present_nos': get_tense(8),
                      'present_eles': get_tense(12),
                      'imperfect_eu': get_tense(16),
                      'imperfect_ele': get_tense(20),
                      'imperfect_nos': get_tense(22),
                      'imperfect_eles': get_tense(26),
                      'preterite_eu': get_tense(44),
                      'preterite_ele': get_tense(48),
                      'preterite_nos': get_tense(50),
                      'preterite_eles': get_tense(54),
                      'future_eu': get_tense(58),
                      'future_ele': get_tense(62),
                      'future_nos': get_tense(64),
                      'future_eles': get_tense(68),
                      'conditional_eu': get_tense(72),
                      'conditional_ele': get_tense(76),
                      'conditional_nos': get_tense(78),
                      'conditional_eles': get_tense(82),
                      'subjunctive_eu': get_tense(86),
                      'subjunctive_ele': get_tense(90),
                      'subjunctive_nos': get_tense(92),
                      'subjunctive_eles': get_tense(96),
                      'gerund': get_tense(157),
                      'past_participle': get_tense(162),
                      }
        PortugueseVerb.objects.filter(vocab=vocab).update(**new_values)
    except AttributeError:
        PortugueseVerb.objects.get(vocab=vocab).delete()


def load_verbs(user):
    pt_verbs = PortugueseVerb.objects.filter(user=user, level__lt=14).exclude(gerund__isnull=True).order_by('?')
    arr = []
    for verb in pt_verbs[:BATCH_SIZE_VERBS]:
        d = {}
        if verb.level // 2 == 0:
            d['eu'] = verb.present_eu
            d['ele'] = verb.present_ele
            d['nós'] = verb.present_nos
            d['eles'] = verb.present_eles
            d['pronouns'] = list(d.keys())
            d['tense'] = 'Presente do indicativo'
            d['info'] = 'things that you usually do'
        elif verb.level // 2 == 1:
            d1, d2 = {}, {}
            d1['eu estou'] = verb.gerund
            d1['ele está'] = verb.gerund
            d1['nós estamos'] = verb.gerund
            d1['eles estão'] = verb.gerund
            d2['eu tenho'] = verb.past_participle
            d2['ele tem'] = verb.past_participle
            d2['nós temos'] = verb.past_participle
            d2['eles têm'] = verb.past_participle
            d = dict(random.sample(d1.items(), 2)) | dict(random.sample(d2.items(), 2))
            d['pronouns'] = list(d.keys())
            d['tense'] = 'Presente contínuo & Pretérito perfeito composto do indicativo'
            d['info'] = 'actions happening right now & repeated actions extending from past into present'
        elif verb.level // 2 == 2:
            d['eu'] = verb.preterite_eu
            d['ele'] = verb.preterite_ele
            d['nós'] = verb.preterite_nos
            d['eles'] = verb.preterite_eles
            d['pronouns'] = list(d.keys())
            d['tense'] = 'Pretérito perfeito do indicativo'
            d['info'] = 'past events that have already happened and are completed'
        elif verb.level // 2 == 3:
            d['eu'] = verb.imperfect_eu
            d['ele'] = verb.imperfect_ele
            d['nós'] = verb.imperfect_nos
            d['eles'] = verb.imperfect_eles
            d['pronouns'] = list(d.keys())
            d['tense'] = 'Pretérito imperfeito do indicativo'
            d['info'] = 'things that used to happen'
        elif verb.level // 2 == 4:
            d['eu'] = verb.future_eu
            d['ele'] = verb.future_ele
            d['nós'] = verb.future_nos
            d['eles'] = verb.future_eles
            d['pronouns'] = list(d.keys())
            d['tense'] = 'Futuro do indicativo'
            d['info'] = 'things that will happen in the future'
        elif verb.level // 2 == 5:
            d['eu'] = verb.conditional_eu
            d['ele'] = verb.conditional_ele
            d['nós'] = verb.conditional_nos
            d['eles'] = verb.conditional_eles
            d['pronouns'] = list(d.keys())
            d['tense'] = 'Condicional'
            d['info'] = 'expressing surprise or uncertainty regarding the future'
        elif verb.level // 2 == 6:
            d['que eu'] = verb.subjunctive_eu
            d['que ele'] = verb.subjunctive_ele
            d['que nós'] = verb.subjunctive_nos
            d['que eles'] = verb.subjunctive_eles
            d['pronouns'] = list(d.keys())
            d['tense'] = 'Presente do subjuntivo'
            d['info'] = 'talking about a possibility or a hypothetical situation'
        d = d | {'id': verb.id, 'level': verb.level, 'infinitive': verb.vocab.word_1, 'translation': verb.vocab.word_2}
        arr.append(d)
    arr_drag_n_drop = list(filter(lambda x: x['level'] % 2 == 0, arr))
    arr_input = list(filter(lambda x: x['level'] % 2 == 1, arr))
    return arr_drag_n_drop + arr_input
