# flake8: noqa

if __import__("typing").TYPE_CHECKING:
    # import apis into api package
    from osparc_client.api.credits_api import CreditsApi
    from osparc_client.api.files_api import FilesApi
    from osparc_client.api.function_job_collections_api import FunctionJobCollectionsApi
    from osparc_client.api.function_jobs_api import FunctionJobsApi
    from osparc_client.api.functions_api import FunctionsApi
    from osparc_client.api.licensed_items_api import LicensedItemsApi
    from osparc_client.api.meta_api import MetaApi
    from osparc_client.api.programs_api import ProgramsApi
    from osparc_client.api.solvers_api import SolversApi
    from osparc_client.api.studies_api import StudiesApi
    from osparc_client.api.tasks_api import TasksApi
    from osparc_client.api.users_api import UsersApi
    from osparc_client.api.wallets_api import WalletsApi
    
else:
    from lazy_imports import LazyModule, as_package, load

    load(
        LazyModule(
            *as_package(__file__),
            """# import apis into api package
from osparc_client.api.credits_api import CreditsApi
from osparc_client.api.files_api import FilesApi
from osparc_client.api.function_job_collections_api import FunctionJobCollectionsApi
from osparc_client.api.function_jobs_api import FunctionJobsApi
from osparc_client.api.functions_api import FunctionsApi
from osparc_client.api.licensed_items_api import LicensedItemsApi
from osparc_client.api.meta_api import MetaApi
from osparc_client.api.programs_api import ProgramsApi
from osparc_client.api.solvers_api import SolversApi
from osparc_client.api.studies_api import StudiesApi
from osparc_client.api.tasks_api import TasksApi
from osparc_client.api.users_api import UsersApi
from osparc_client.api.wallets_api import WalletsApi

""",
            name=__name__,
            doc=__doc__,
        )
    )
