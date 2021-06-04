import ecdsa
import random
import libnum
import hashlib
import base64
from urllib.parse import unquote

def parse_element(hex_str, offset, element_size):
    """
    :param hex_str: string to parse the element from.
    :type hex_str: hex str
    :param offset: initial position of the object inside the hex_str.
    :type offset: int
    :param element_size: size of the element to extract.
    :type element_size: int
    :return: The extracted element from the provided string, and the updated offset after extracting it.
    :rtype tuple(str, int)
    """

    return hex_str[offset:offset+element_size], offset+element_size

def dissect_signature(hex_sig):
    """
    Extracts the r, s and ht components from a ECDSA signature Commonly used by Bitcoin.
    :param hex_sig: Signature in  hex format.
    :type hex_sig: hex str
    :return: r, s, t as a tuple.
    :rtype: tuple(str, str, str)
    """

    offset = 0
    # Check the sig contains at least the size and sequence marker
    assert len(hex_sig) > 4, "Wrong signature format."
    sequence, offset = parse_element(hex_sig, offset, 2)
    # Check sequence marker is correct
    assert sequence == '30', "Wrong sequence marker."
    signature_length, offset = parse_element(hex_sig, offset, 2)
    # Check the length of the remaining part matches the length of the signature + the length of the hashflag (1 byte)
    assert len(hex_sig[offset:])/2 == int(signature_length, 16) - 0, "Wrong length."	#You might want to change the final value to suite your signature length. i.e: '0'
    # Get r
    marker, offset = parse_element(hex_sig, offset, 2)
    assert marker == '02', "Wrong r marker."
    len_r, offset = parse_element(hex_sig, offset, 2)
    len_r_int = int(len_r, 16) * 2   # Each byte represents 2 characters
    r, offset = parse_element(hex_sig, offset, len_r_int)
    # Get s
    marker, offset = parse_element(hex_sig, offset, 2)
    assert marker == '02', "Wrong s marker."
    len_s, offset = parse_element(hex_sig, offset, 2)
    len_s_int = int(len_s, 16) * 2  # Each byte represents 2 characters
    s, offset = parse_element(hex_sig, offset, len_s_int)
    # Get ht
    ht, offset = parse_element(hex_sig, offset, 0)	#Change the value here to reflect the same value changed above in the Length check part. i.e: '0'
    assert offset == len(hex_sig), "Wrong parsing."

    return r, s, ht


def keyRetrieval(m1,m2,r1,s1,r2,s2):

    G = ecdsa.SECP256k1.generator
    order = G.order()

    #Convert the message within the cookies to hash
    h1 = int(hashlib.sha256(m1.encode()).hexdigest(),base=16)
    h2 = int(hashlib.sha256(m2.encode()).hexdigest(),base=16)

    #Convert the r and s values to int from hex
    Conv_r1,Conv_s1 = int(r1, 16), int(s1, 16)
    Conv_r2,Conv_s2 = int(r2, 16), int(s2, 16)

    valinv = libnum.invmod(Conv_r1*(Conv_s1-Conv_s2),order)
    priv_key = ((Conv_s2*h1-Conv_s1*h2) * (valinv)) % order

    return priv_key

def main():

    print ("\n\t*************** ECDSA Private Key Retriever ***************\n\n")
    print ("--- Make sure to create two signature with messages of same length. i.e: username1 = admin and username2 = qwert ---\n\n")
    print ("-- This tool is for SECP256k1 curve --\n")
    cookies = input("Enter two cookies seperated by a space: \n\n")
    cookie1, cookie2 = cookies.split(" ")

    user1, signature1 = base64.b64decode(unquote(cookie1)).split(b"--")
    user2, signature2 = base64.b64decode(unquote(cookie2)).split(b"--")
    converted_signature1 = signature1.hex()
    converted_signature2 = signature2.hex()
    sig1 = converted_signature1
    sig2 = converted_signature2
    r1, s1, ht1 = dissect_signature(sig1)
    r2, s2, ht2 = dissect_signature(sig2)

    priv_key = keyRetrieval(user1.decode("utf-8"),user2.decode("utf-8"),r1,s1,r2,s2)
    print ("\nSuccess!! \n\nPrivate Key is: ",priv_key, "\n")

if __name__ == "__main__":
	main()
