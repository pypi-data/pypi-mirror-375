from vents.connections import (
    BucketConnection,
    ClaimConnection,
    Connection,
    ConnectionResource,
    GitConnection,
    HostConnection,
    HostPathConnection,
)

from polyaxon._schemas.base import BaseSchemaModel
from polyaxon._schemas.types.base import BaseTypeConfig


class V1BucketConnection(BucketConnection, BaseSchemaModel):
    pass


class V1ClaimConnection(ClaimConnection, BaseSchemaModel):
    pass


class V1GitConnection(GitConnection, BaseSchemaModel):
    pass


class V1HostConnection(HostConnection, BaseSchemaModel):
    pass


class V1HostPathConnection(HostPathConnection, BaseSchemaModel):
    pass


class V1ConnectionResource(ConnectionResource, BaseSchemaModel):
    pass


class V1Connection(Connection, BaseTypeConfig):
    """Connections are how Polyaxon connects several
    types of external systems and resources to your operations.

    All connections in Polyaxon are typed, and some of them have special built-in handlers
    to automatically connect and load information.

    Using connections you can define the boilerplate required
    to connect a volume, a blob storage once, secret definition for loading data from a data source.
    Rnd users, e.g. data scientist, can just reference the name of the connection to use it
    without dealing with the configuration every time.

    Connections are not required to mount secrets or configurations,
    in fact users can also mount secrets and volumes the Kubernetes way,
    but this mean you are exposing the service to very few team members who have
    the Kubernetes know-how, in some advance use-cases,
    you will have to leverage the low level Kubernetes API,
    but for most interactions, using the connection specification is much simpler,
    similar to how easy it is to define service accounts or image pull secrets instead of
    defining all the volumes and mounting them to the containers manually.

    For some distributions, Polyaxon will expose:
        * Analytics about how often connections are used.
        * Jobs that requested those connections.
        * Profiling and runtime metadata to optimize access to those resources and connections.
        * Additional RBAC and ACL rules to control who can access the connections.

    Args:
         name: str
         description: str, optional
         tags: List[str], optional
         kind: str, Union[`host_path`, `volume_claim`, `gcs`, `s3`, `wasb`, `registry`, `git`,
                          `aws`, `gcp`, `azure`, `mysql`, `postgres`, `oracle`, `vertica`,
                          `sqlite`, `mssql`, `redis`, `presto`, `mongo`, `cassandra`, `ftp`,
                          `grpc`, `hdfs`, `http`, `pig_cli`, `hive_cli`, `hive_metastore`,
                          `hive_server2`, `jdbc`, `jenkins`, `samba`, `snowflake`, `ssh`,
                          `cloudant`, `databricks`, `segment`, `slack`, `discord`, `mattermost`,
                          `pagerduty`, `hipchat`, `webhook`, `custom`]
        schema: dict, optional
        secret: str, optional
        config_map: str, optional
        env: List[Dict], optional
        annotations: Dict, optional


    ## YAML usage

    ```yaml
    >>> artifactsStore:
    >>>   name: azure
    >>>   kind: wasb
    >>>   schema:
    >>>     bucket: "wasbs://test@container.blob.core.windows.net/"
    >>>   secret:
    >>>     name: "az-secret"
    >>> connections:
    >>>   - name: repo-test
    >>>     description: "some description"
    >>>     tags: ["tag1", "tag2"]
    >>>     kind: git
    >>>     schema:
    >>>       url: https://gitlab.com/org/test
    >>>     secret:
    >>>       name: "gitlab-connection"
    >>>   - name: docker-connection
    >>>     description: "some description"
    >>>     kind: registry
    >>>     schema:
    >>>       url: org/repo
    >>>     secret:
    >>>       name: docker-conf
    >>>       mountPath: /kaniko/.docker
    >>>   - name: my-slack
    >>>     kind: slack
    >>>     secret:
    >>>       name: my-slack
    ```

    ## Fields

    ### name

    The connection name must be unique within an organization.
    User can use this unique name to reference a connection in their components and operations.

    An end user does not need to know about how to mount secrets and configurations
    to access a dataset for example, they can just reference the name of the connection.

    ### description

    A short description about the purpose of the connection for other users.

    For example, "s3 bucket with radio images"

    ### tags

    Tags to categorize the connection in the connections catalog table.

    ### kind

    the kind of the connection. Apart from the fact that Polyaxon
    has built-in handlers for several connections, user can build their own handlers,
    for example you can create a handler for pulling data from a database
    or a data lake based on a specific kind.

    Polyaxon will show a small connection logo for some types in the
    dashboard and analytics about the connection usage.

    Polyaxon exposes this list of connection kinds:
    [`host_path`, `volume_claim`, `gcs`, `s3`, `wasb`, `registry`, `git`, `aws`,
     `gcp`, `azure`, `mysql`, `postgres`, `oracle`, `vertica`,
     `sqlite`, `mssql`, `redis`, `presto`, `mongo`, `cassandra`, `ftp`,
     `grpc`, `hdfs`, `http`, `pig_cli`, `hive_cli`, `hive_metastore`,
     `hive_server2`, `jdbc`, `jenkins`, `samba`, `snowflake`, `ssh`,
     `cloudant`, `databricks`, `segment`, `slack`, `discord`, `mattermost`,
     `pagerduty`, `hipchat`, `webhook`, `custom`]

    Polyaxon can also automatically handle these connection kinds:
    [`host_path`, `volume_claim`, `gcs`, `s3`, `wasb`, `registry`, `git`]

    ### schema

    In order to leverage some built-in functionalities in Polyaxon,
    e.g. automatic management of outputs, initializers for cloning code from git repos,
    loading data from S3/GCS/Azure/Volumes/Paths, or pushing container images to a registry,
    the schema is how Polyaxon knows how to authenticate the containers that will handle that logic.

    If you opt-out of using those functionalities, you can leave this field empty or
    you can expose any key/value object you want for your own custom handlers.

    For more details please check connection schema section for the built-in handlers:
        * [artifacts connections](/docs/setup/connections/artifacts/)
        * [git connections](/docs/setup/connections/git/)
        * [docker registry connections](/docs/setup/connections/registry/)

    ### secret

    We assume that each connection will only need to access to at most one secret.
    If you are building a specific handler for a connection,
    this is where you will need to expose the necessary paths or environment variables needed
    to make the http/grpc connection.

    In many cases you might not need to expose any secret, for instance for volumes and host paths.

    The connection secret schema has 3 fields:

        * name: str, required, the name of the secret,
                this is the minimum to tell Polyaxon to mount that secret
                whenever the connection is referenced.
        * mountPath: str, optional, if you prefer to mount the secret as a volume
                     instead of exposing its items as environment variables.
        * items: List[str], optional, if you only want to expose a subset
                 of the items in the secret.

    Example slack connection

    ```yaml
    >>> name: my-slack
    >>> kind: slack
    >>> secret:
    >>>   name: my-slack
    ```

    Example docker connection with mountPath

    ```yaml
    >>> kind: registry
    >>> schema:
    >>>   url: registry.com/org/repo
    >>> secret:
    >>>   name: docker-conf
    >>>   mountPath: /kaniko/.docker
    ```

    ### configMap

    We assume that each connection will only need to access to at most one config map.
    Similar logic for the secret, if you need to expose more information to connect to a service,
    you can reference a config map.

    In many cases you might not need to expose any config map.

    The connection configMap schema has 3 fields:

        * name: str, required, the name of the configMap,
                this is the minimum to tell Polyaxon to mount that configMap
                whenever the connection is referenced.
        * mountPath: str, optional, if you prefer to mount the configMap as a volume
                     instead of exposing its items as environment variables.
        * items: List[str], optional, if you only want to expose a subset
                 of the items in the configMap.

    ### env

    > **Note**: This is available starting from v1.18

    Optional list of environment variables to always inject with the connection.

    Example

    ```yaml
    >>> name: ...
    >>> kind: ...
    >>> secret:
    >>>   name: ...
    >>> env:
    >>>   - name: KEY1
    >>>     value: VALUE1
    >>>   - name: KEY2
    >>>     value: VALUE2
    ```

    ### annotations

    > **Note**: This is available starting from v1.18

    A list of annotations to always use with the connection.

    From [Kubernetes docs](https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/)  # noqa

    > You can use Kubernetes annotations to attach arbitrary non-identifying metadata to objects.
    > Clients such as tools and libraries can retrieve this metadata.

    ```yaml
    >>> annotations:
    >>>   key1: "value1"
    >>>   key2: "value2"
    """


# Backwards compatibility
V1ConnectionType = V1Connection
V1ConnectionResourceType = V1ConnectionResource
