import graphene
from crm.schema import Query as CRMQuery, Mutation as CRMMutation

class Query(CRMQuery, graphene.ObjectType):
    # The hello field is already defined in CRMQuery, so we inherit it
    pass

class Mutation(CRMMutation, graphene.ObjectType):
    pass

# Only define the schema once with both query and mutation
schema = graphene.Schema(query=Query, mutation=Mutation)
