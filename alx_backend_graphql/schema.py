import graphene 
from crm.schema import Query as CRMQuery, Mutation as CRMMutation

class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, world!")

schema = graphene.Schema(query=Query)

class Query(CRMQuery, graphene.ObjectType):
    pass

class Mutation(CRMMutation, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)

import graphene
import crm.schema

class Query(crm.schema.Query, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query)
