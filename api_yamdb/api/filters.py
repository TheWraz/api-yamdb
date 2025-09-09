import django_filters

from reviews.models import Title


class TitleFilter(django_filters.FilterSet):
    """Фильтры для произведений по жанру, категории, названию и году выпуска"""

    genre = django_filters.CharFilter(
        field_name='genre__slug',
        lookup_expr='exact'
    )
    category = django_filters.CharFilter(
        field_name='category__slug',
        lookup_expr='exact'
    )
    name = django_filters.CharFilter(
        lookup_expr='icontains'
    )
    year = django_filters.NumberFilter()

    class Meta:
        model = Title
        fields = ['genre', 'category', 'name', 'year']
# Когда объявляется коллекция, нужно верно выбрать между списком и кортежем(тут список). 
# Выбор нужно делать осознанно, потому что список изменяемый, а кортеж нет. 
# Если предполагается, что сюда будет вноситься изменения где то в коде, то нужен список, а если изменений никаких не будет то лучше кортеж.
# Тут и далее.