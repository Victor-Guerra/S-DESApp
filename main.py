IP = [2,6,3,1,4,8,5,7]
IPINV = [4,1,3,5,7,2,8,6]
P4 = [2,4,3,1]
P8 = [6,3,7,4,8,5,10,9]
P10 = [3,5,2,7,4,10,1,9,8,6]
EP = [4,1,2,3,2,3,4,1]
S0 = [[1,0,3,2], [3,2,1,0], [0,2,1,3], [3,1,3,2]]
S1 = [[0,1,2,3], [2,0,1,3], [3,0,1,0], [2,1,0,3]]

def permute(original_string, key):
    permuted_characters = []
    for i in range(0, len(key), 1):
        permuted_characters.append(original_string[key[i]-1])
    
    permuted_string = "".join(permuted_characters) 
    return permuted_string
    
def left_shift(shifting_string, shift_value):
    shifted_characters = []
    string_size = len(shifting_string)
    for i in range(0, string_size, 1):
        if (i+shift_value) < string_size:
            shifted_characters.append(shifting_string[i+shift_value])
        else:
            shifted_characters.append(shifting_string[i+shift_value-string_size])
    
    shifted_string = "".join(shifted_characters)
    
    return shifted_string

def obtain_subkeys(main_key):
#   Se calcula la P10 de main_key
    P10_of_main_key = permute(main_key, P10)
#   Se realiza el CLS a ambas mitades de P10(main_key)
    CLS_of_P10 = left_shift(P10_of_main_key[:len(P10_of_main_key)//2], 1) + left_shift(P10_of_main_key[len(P10_of_main_key)//2:], 1)
#   Se realiza P8 del resultado anterior y se obtiene la subllave 1
    Subkey1 = permute(CLS_of_P10, P8)
#   Se realizan otros 2 CLS a ambas mitades de P10(main_key)
    CLS_of_P10_pt2 = left_shift(CLS_of_P10[:len(CLS_of_P10)//2], 2) + left_shift(CLS_of_P10[len(CLS_of_P10)//2:], 2)
#   Se realiza P8 al resultado anterior y se obtiene la subllave 2
    Subkey2 = permute(CLS_of_P10_pt2, P8)

    return (Subkey1, Subkey2)

def xor_compare(string1, string2):
    if len(string1) != len(string2):
        print('Strings are of unequal length')
        print('@ xor_compare')
        exit()
    result = [ 0 if x==y else 1 for (x,y) in zip(string1,string2) ]
    return result

#   Para aplicar el algoritmo con matrices s0 y s1
def apply_matrix(string, matrix):
    row = int(string[0] + string[3], 2)
    col = int(string[1] + string[2], 2)
    result = str(bin(matrix[row][col]))[2:]
    if result == '0':
        result = result + '0'
    elif result == '1':
        result = '0' + result
    return result

# Apply the general loop of fk to an initially permutated plain text
def apply_f_k(initial_permutation, subkey):
    ptL = initial_permutation[:4]
    ptR = initial_permutation[4:]
#   Se obtiene E/P del lado derecho de IP(plain_text)
    EPofR = permute(ptR, EP)
    print('E/P of R: ', EPofR)
#   Se realiza XOR entre el resultado anterior y la subllave1
    EPxorK = xor_compare(EPofR, subkey)
    print('E/P xor key: ', EPxorK)
    L4xor = EPxorK[:4]
    L4xor = ''.join(str(e) for e in L4xor)
    R4xor = EPxorK[4:]
    R4xor = ''.join(str(e) for e in R4xor)
    print('L4  after xor: ', L4xor)
    print('R4  after xor: ', R4xor)
#   Se aplica S0 a L4 y S1 a R4
    S0_of_L4 = apply_matrix(L4xor, S0)
    S1_of_R4 = apply_matrix(R4xor, S1)
    
    print(S0_of_L4, S1_of_R4)
#   Se aplica P4 a la concatenacion de ambos resultados anteriores
    P4_of_s0_s1 = permute(S0_of_L4 + S1_of_R4, P4)
    print('P4(s0 + s1): ', P4_of_s0_s1)
#   Se Aplica xor a ptL con el resultado anterior
    ptL_xor_P4 = ''.join( str(e) for e in xor_compare(ptL, P4_of_s0_s1))
#   Se obtiene el SW
    return ptL_xor_P4 + ptR

#Empieza aqui el Simplified-DES, el plaintext se podría recibir por input. pkey es la llave para la permutacion de 10.
plaintext = '0000010011'
pkey = [3,5,2,7,4,10,1,9,8,6]
pstring = permute(plaintext, pkey)

#Aqui se hace el left-shift para ambas mitades de la cadena. pkey2 es para hacer la permutacion de 8 al concatenar ambas mitades
concatenaded_string1 = left_shift(pstring[:len(pstring)//2], 1) + left_shift(pstring[len(pstring)//2:], 1)
pkey2 = [4,1,5,2,6,3,8,7]
primera_llave = permute(concatenaded_string1[2:], pkey2)
#print('Primer resultado: ', primer_resultado)

#Se usa el resultado no permutado anterior para hacer otra vez doble left-shift para obtener la segunda permutacion de 8 
concatenaded_string2 = left_shift(concatenaded_string1[:len(concatenaded_string1)//2], 2) + left_shift(concatenaded_string1[len(concatenaded_string1)//2:], 2)
segunda_llave = permute(concatenaded_string2[2:], pkey2)
#print('Segundo resultado: ', segundo_resultado)

if __name__ == "__main__": 
    main_key =  '1010000010'
    plain_text =  '10010111'

    if len(plain_text) != 8 or len(main_key) != 10:
        print("Either the main key or the plain text are of unadequate legth.")
        exit()
#   Se obtiene el par de subllaves
    sk1, sk2 = obtain_subkeys(main_key)

#   Se realiza la permutacion inicial al plaintext
    IPplain_text = permute(plain_text, IP)

#   Se aplica fk1 sobre la permutacion inicial del plain text
    preSW = apply_f_k(IPplain_text, sk1)
    SW = preSW[4:] + preSW[:4]
    print(SW)

#   Se aplica fk2 sobre el SW obtenido y se obtiene el pre-cipher text
    preCT = apply_f_k(SW, sk2)
    print(preCT)
#   Se aplica la IP inversa, para obtener el verdadero Cipher Text
    cipher_text = permute(preCT, IPINV)
    print('Cipher Text: ', cipher_text)
