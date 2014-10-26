"""
Support for EC keypair operation missing form public libcrypto API
"""
from ctypescrypto.pkey import PKey, PKeyError
from ctypes import c_void_p,c_char_p,c_int,byref
from ctypescrypto import libcrypto

def create(curve,data):
	"""
		Creates EC keypair from the just secret key and curve name
		
		@param curve - name of elliptic curve
		@param num - long number representing key
	"""
	ec=libcrypto.EC_KEY_new_by_curve_name(curve.nid)
	if ec is None:	
		raise PKeyError("EC_KEY_new_by_curvename")
	group=libcrypto.EC_KEY_get0_group(ec)
	if group is None:
		raise PKeyError("EC_KEY_get0_group")
	libcrypto.EC_GROUP_set_asn1_flag(group,1)
	raw_key=libcrypto.BN_new()
	if raw_key is None:
		raise PKeyError("BN_new")
	ctx=libcrypto.BN_CTX_new()
	if ctx is None:
		raise PKeyError("BN_CTX_new")
	if libcrypto.BN_bin2bn(data,len(data),raw_key) is None:
		raise PKeyError("BN_bin2bn")
	order=libcrypto.BN_new()
	if order is None:
		raise PKeyError("BN_new")
	priv_key = libcrypto.BN_new()
	if priv_key is None:
		raise PKeyError("BN_new")
	if libcrypto.EC_GROUP_get_order(group,order,ctx) <=0:
		raise PKeyError("EC_GROUP_get_order")
	if libcrypto.BN_nnmod(priv_key,raw_key,order,ctx) <=0:
		raise PKeyError("BN_nnmod")
	if libcrypto.EC_KEY_set_private_key(ec,priv_key)<=0:
		raise PKeyError("EC_KEY_set_private_key")
	pub_key=libcrypto.EC_POINT_new(group)
	if pub_key is None:
		raise PKeyError("EC_POINT_new")
	if libcrypto.EC_POINT_mul(group,pub_key,priv_key,None,None,ctx)<=0:
		raise PKeyError("EC_POINT_mul")
	if libcrypto.EC_KEY_set_public_key(ec,pub_key)<=0:
		raise PKeyError("EC_KEY_set_public_key")
	libcrypto.BN_free(raw_key)
	libcrypto.BN_free(order)
	libcrypto.BN_free(priv_key)
	libcrypto.BN_CTX_free(ctx)
	p=libcrypto.EVP_PKEY_new()
	if p is None:
		raise PKeyError("EVP_PKEY_new")	
	if libcrypto.EVP_PKEY_set1_EC_KEY(p,ec)<=0:
		raise PKeyError("EVP_PKEY_set1_EC_KEY")
	libcrypto.EC_KEY_free(ec)
	return PKey(ptr=p,cansign=True)


libcrypto.EVP_PKEY_new.restype=c_void_p
libcrypto.BN_new.restype=c_void_p
libcrypto.BN_free.argtypes=(c_void_p,)
libcrypto.BN_CTX_new.restype=c_void_p
libcrypto.BN_CTX_free.argtypes=(c_void_p,)
libcrypto.BN_bin2bn.argtypes=(c_char_p,c_int,c_void_p)
libcrypto.EC_KEY_set_private_key.argtypes=(c_void_p,c_void_p)
libcrypto.EC_POINT_new.argtypes=(c_void_p,)
libcrypto.EC_POINT_new.restype=c_void_p
libcrypto.EC_POINT_mul.argtypes=(c_void_p,c_void_p,c_void_p,c_void_p,c_void_p,c_void_p)
libcrypto.EC_KEY_set_public_key.argtypes=(c_void_p,c_void_p)


