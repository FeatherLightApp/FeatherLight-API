from ariadne import MutationType

MUTATION = MutationType()

@MUTATION.field('bakeMacaroon')
def r_bake_macaroon(user: User, *_, caveats: List[str]):
    return caveats