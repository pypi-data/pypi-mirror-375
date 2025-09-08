from .data_structures import *
from .search_algorythms import *
from .additional_funcs import *
from ..forall import *

data1 = text1.split('abracadabrabibidi')
data_structures_dict = dict([(x.split('\n')[1].replace("# ", ""), x) for x in data1])
data2 = text2.split('abracadabrabibidi')
search_algorythms_dict = dict([(x.split('\n')[1].replace("# ", ""), x) for x in data2])
data3 = text3.split('abracadabrabibidi')
additional_funcs_dict = dict([(x.split('\n')[1].replace("# ", ""), x) for x in data3])

themes = {
    'Структуры данных': list(data_structures_dict.keys()),
    'Алгоритмы сортировки': list(search_algorythms_dict.keys()),
    'Дополнительные функции': list(additional_funcs_dict.keys())
}

# Новый словарь, аналогичный themes_list_dicts_full из второго примера
themes_list_dicts_full = {
    'Структуры данных': data_structures_dict,
    'Алгоритмы сортировки': search_algorythms_dict,
    'Дополнительные функции': additional_funcs_dict
}

# Тема -> Выбор структуры -> структура
def description(dict_to_show=themes, key=None, show_only_keys: bool = True, to_print=True):
    if isinstance(dict_to_show, str) and dict_to_show != 'Вывести функцию буфера обмена' and key is None:
        # Используем themes_list_dicts_full для получения нужного словаря по теме
        dict_to_show = themes_list_dicts_full[dict_to_show]
        text = ""
        length1 = 1 + max([len(x) for x in dict_to_show.keys()])
        for key in dict_to_show.keys():
            text += f'{key:<{length1}}\n'
        return print(text) if to_print else text

    elif isinstance(dict_to_show, str) and dict_to_show != 'Вывести функцию буфера обмена' and key in themes_list_dicts_full[dict_to_show].keys():
        return print(themes_list_dicts_full[dict_to_show][key]) if to_print else themes_list_dicts_full[dict_to_show][key]
    else:
        show_only_keys = False

    text = ""
    length1 = 1 + max([len(x) for x in dict_to_show.keys()])
    for key in dict_to_show.keys():
        text += f'{key:^{length1}}'
        if not show_only_keys:
            text += ': '
            for f in dict_to_show[key]:
                text += f'{f};\n' + ' ' * (length1 + 2)
        text += '\n'
    return print(text) if to_print else text
