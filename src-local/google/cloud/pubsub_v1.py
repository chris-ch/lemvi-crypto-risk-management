from flask import current_app


class DummyFuture(object):
    def result(self):
        pass


class PublisherClient(object):
    """
    Dummy class for publishing locally.
    """

    def topic_path(self, google_cloud_project, topic_name):
        return 'dummy-{}-{}'.format(google_cloud_project, topic_name)

    def publish(self, topic_path, param, origin=None):
        current_app.logger.info('publishing message to topic {}: {}'.format(topic_path, param))
        return DummyFuture()