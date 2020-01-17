# from ariadne import ObjectType

# local_invoice = ObjectType('LocalInvoice')
# feature = ObjectType('Feature')
# features_entry = ObjectType('FeaturesEntry')
# hop_hint = ObjectType('HopHint')
# route_hint = ObjectType('RouteHint')

# @local_invoice.field('destination')
# def r_destination(obj, info):
#     return obj.destination

# @local_invoice.field('paymentHash')
# def r_payment_hash(obj, info):
#     return obj.payment_hash

# @local_invoice.field('numSatoshis')
# def r_num_satoshis(obj, info):
#     return obj.num_satoshis

# @local_invoice.field('timestamp')
# def r_timestamp(obj, info):
#     return int(obj.timestamp)

# @local_invoice.field('expiry')
# def r_expiry(obj, info):
#     return int(obj.expiry)

# @local_invoice.field('description')
# def r_description(obj, info):
#     return obj.description

# @local_invoice.field('fallbackAddress')
# def r_fallback_address(obj, info):
#     return obj.fallback_addr

# @local_invoice.field('cltvExpiry')
# def r_cltv_expiry(obj, info):
#     return int(obj.cltv_expiry)

# @local_invoice.field('routeHints')
# def r_route_hints(obj, info):
#     return obj.route_hints

# @local_invoice.field('paymentAddress')
# def r_payment_address(obj, info):
#     return obj.payment_addr

# @local_invoice.field('features')
# def r_features(obj, info):
#     return obj.features


# @feature.field('name')
# def r_name(obj, info):
#     return obj.name

# @feature.field('isRequired')
# def r_is_required(obj, info):
#     return obj.is_required

# @feature.field('isKnown')
# def r_return(obj, info):
#     return obj.is_known

# @features_entry.field('key')
# def r_key(obj, info):
#     return obj.key

# @features_entry.field('value')
# def r_value(boj, info):
#     return obj.value

# @route_hint.field('hopHints')
# def r_hop_hint(obj, info):
#     return obj.hop_hints

# @hop_hint.field('nodeID')
# def r_node_id(obj, info):
#     return obj.node_id

# @hop_hint.field('chanID')
# def r_chan_id(obj, info):
#     return int(obj.chan_id)

# @hop_hint.field('feeBaseMsat')
# def r_fee_base_msat(obj, info):
#     return int(obj.fee_base_msat)

# @hop_hint.field('feePropMilionth')
# def r_fee_prop_milionth(obj, info):
#     return int(obj.fee_proportional_millionths)

# @hop_hint.field('cltvExpiryDelta')
# def r_cltv_expiry_delta(obj, info):
#     return int(obj.cltv_expiry_delta)
