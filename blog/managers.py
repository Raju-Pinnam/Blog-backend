from django.db.models import Manager


class PublishedManager(Manager):
    """ Custom Model Manger For Posts Model

    """

    def get_queryset(self):
        """ query set of posts
            which were status set to published only
        Returns:
            objeccts: posts 
        """
        return super(PublishedManager, self).get_queryset().filter(status='published')
