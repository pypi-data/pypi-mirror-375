
from dependency_injector import containers, providers

import pulumi_kubernetes as k8s

def get_kubeconfig(core):
    kubeconfig = core.base_stack().get_output("kubeconfig")
    core.exports()['kubeconfig'] = kubeconfig
    return kubeconfig


class Kubernetes(containers.DeclarativeContainer):

    core = providers.DependenciesContainer()

    kubeconfig = providers.Singleton(
        get_kubeconfig,
        core=core
    )

    namespace = providers.Factory(
        core.get_stack_var,
        "namespace",
    )

    namespaced_provider = providers.Singleton(
        k8s.Provider,
        "k8s-provider",
        kubeconfig=kubeconfig,
        namespace=namespace,
    )

    cluster_provider = providers.Singleton(
        k8s.Provider,
        "k8s-cluster-provider",
        kubeconfig=kubeconfig,
    )