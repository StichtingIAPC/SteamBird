from django.forms.widgets import Widget

# pylint: disable=invalid-name
_ba_tmp = Widget.build_attrs


def _ba(self, base_attrs, extra_attrs=None):
    if extra_attrs and 'class' in extra_attrs:
        extra_attrs = extra_attrs.copy()
        extra_attrs['class'] += ' form-control'
    else:
        base_attrs = base_attrs.copy()
        base_attrs['class'] = base_attrs.get('class', '') + ' form-control'

    if extra_attrs and 'style' in extra_attrs:
        extra_attrs = extra_attrs.copy()
        extra_attrs['style'] += ';width:auto;display:inline;'
    else:
        base_attrs = base_attrs.copy()
        base_attrs['style'] = base_attrs.get('style', '') + \
                              ';width:auto;display:inline;'

    return _ba_tmp(self, base_attrs, extra_attrs)


Widget.build_attrs = _ba
