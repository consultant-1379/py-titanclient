The `titanclient.api` submodule provides a simplifying wrapper over the
DsREST API of TitanSim.

`client.Client` can query a current execution for statistics and other
runtime information and modify runtime values such as CPS/RPS and the like.

TitanSim requests have a fairly powerful but rather convoluted format
that is difficult to assemble by hand and the responses returned are
also heavily hierarchical. To simplify the process of creating request
objects, a `DsRequest` class is provided for this purpose.

The DsREST API itself exposes a hierarchy of entity groups, scenario
groups, scenarios and traffic cases. The configuration, on the other
hand, keeps tabs on scenarios and traffic cases, which - roughly -
correspond to scenario groups and scenarios in the DsREST API.

It wouldn't help the goal of simplification if this mismatch were to
be propagated at a higher level by using both models. Instead, we do
the next worst thing: we add a new one. Currently (that is, until a
better idea comes along), the `Scenario` abstraction, a severe,
possibly broken oversimplification is used in this library.

