from sys import argv
IP = [2, 6, 3, 1, 4, 8, 5, 7]      # Initial Permutation
IPINV = [4, 1, 3, 5, 7, 2, 8, 6]   # Inverse Initial Permutation
P4 = [2, 4, 3, 1]
P8 = [6, 3, 7, 4, 8, 5, 10, 9]
P10 = [3, 5, 2, 7, 4, 10, 1, 9, 8, 6]
EP = [4, 1, 2, 3, 2, 3, 4, 1]      # Expanded Permutation
S0 = [[1, 0, 3, 2], [3, 2, 1, 0], [0, 2, 1, 3], [3, 1, 3, 2]]   # S-Box
S1 = [[0, 1, 2, 3], [2, 0, 1, 3], [3, 0, 1, 0], [2, 1, 0, 3]]   # S-Box


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
            shifted_characters.append(
                shifting_string[i+shift_value-string_size])

    shifted_string = "".join(shifted_characters)

    return shifted_string


def obtain_subkeys(main_key):
    #   Se calcula la P10 de main_key
    P10_of_main_key = permute(main_key, P10)
#   Se realiza el CLS a ambas mitades de P10(main_key)
    CLS_of_P10 = left_shift(P10_of_main_key[:len(
        P10_of_main_key)//2], 1) + left_shift(P10_of_main_key[len(P10_of_main_key)//2:], 1)
#   Se realiza P8 del resultado anterior y se obtiene la subllave 1
    Subkey1 = permute(CLS_of_P10, P8)
#   Se realizan otros 2 CLS a ambas mitades de P10(main_key)
    CLS_of_P10_pt2 = left_shift(CLS_of_P10[:len(
        CLS_of_P10)//2], 2) + left_shift(CLS_of_P10[len(CLS_of_P10)//2:], 2)
#   Se realiza P8 al resultado anterior y se obtiene la subllave 2
    Subkey2 = permute(CLS_of_P10_pt2, P8)

    return (Subkey1, Subkey2)


def xor_compare(string1, string2):
    if len(string1) != len(string2):
        print('Strings are of unequal length')
        print('@ xor_compare')
        exit()
    result = [0 if x == y else 1 for (x, y) in zip(string1, string2)]
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
#   Se realiza XOR entre el resultado anterior y la subllave1
    EPxorK = xor_compare(EPofR, subkey)
    L4xor = EPxorK[:4]
    L4xor = ''.join(str(e) for e in L4xor)
    R4xor = EPxorK[4:]
    R4xor = ''.join(str(e) for e in R4xor)
#   Se aplica S0 a L4 y S1 a R4
    S0_of_L4 = apply_matrix(L4xor, S0)
    S1_of_R4 = apply_matrix(R4xor, S1)

#   Se aplica P4 a la concatenacion de ambos resultados anteriores
    P4_of_s0_s1 = permute(S0_of_L4 + S1_of_R4, P4)
#   Se Aplica xor a ptL con el resultado anterior
    ptL_xor_P4 = ''.join(str(e) for e in xor_compare(ptL, P4_of_s0_s1))
#   Se obtiene el SW
    return ptL_xor_P4 + ptR

# Apply the general loop of fk to an initially permutated plain text


def apply_f_k_verbose(initial_permutation, subkey):
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
    ptL_xor_P4 = ''.join(str(e) for e in xor_compare(ptL, P4_of_s0_s1))
#   Se obtiene el SW
    return ptL_xor_P4 + ptR


def encriptar(main_key, plain_text):
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

#   Se aplica fk2 sobre el SW obtenido y se obtiene el pre-cipher text
    preCT = apply_f_k(SW, sk2)
#   Se aplica la IP inversa, para obtener el verdadero Cipher Text
    cipher_text = permute(preCT, IPINV)
    return cipher_text


def encriptar_verbose(main_key, plain_text):
    if len(plain_text) != 8 or len(main_key) != 10:
        print("Either the main key or the plain text are of unadequate legth.")
        exit()
#   Se obtiene el par de subllaves
    sk1, sk2 = obtain_subkeys(main_key)

#   Se realiza la permutacion inicial al plaintext
    IPplain_text = permute(plain_text, IP)

#   Se aplica fk1 sobre la permutacion inicial del plain text
    preSW = apply_f_k_verbose(IPplain_text, sk1)
    SW = preSW[4:] + preSW[:4]
    print(SW)

#   Se aplica fk2 sobre el SW obtenido y se obtiene el pre-cipher text
    preCT = apply_f_k_verbose(SW, sk2)
    print(preCT)
#   Se aplica la IP inversa, para obtener el verdadero Cipher Text
    cipher_text = permute(preCT, IPINV)
    print('Cipher Text: ', cipher_text)
    return cipher_text


def desencriptar(main_key, cipher_text):
    if len(cipher_text) != 8 or len(main_key) != 10:
        print("Either the main key or the cipher text are of unadequate legth.")
        exit()
#   Se obtiene el par de subllaves
    sk1, sk2 = obtain_subkeys(main_key)

#   Se realiza la permutacion inicial al plaintext
    IPcipher_text = permute(cipher_text, IP)

#   Se aplica fk1 sobre la permutacion inicial del plain text
    preSW = apply_f_k(IPcipher_text, sk2)
    SW = preSW[4:] + preSW[:4]

#   Se aplica fk2 sobre el SW obtenido y se obtiene el pre-cipher text
    preCT = apply_f_k(SW, sk1)
#   Se aplica la IP inversa, para obtener el verdadero Cipher Text
    plain_text = permute(preCT, IPINV)
    return plain_text


def desencriptar_verbose(main_key, cipher_text):
    if len(cipher_text) != 8 or len(main_key) != 10:
        print("Either the main key or the cipher text are of unadequate legth.")
        exit()
#   Se obtiene el par de subllaves
    sk1, sk2 = obtain_subkeys(main_key)

#   Se realiza la permutacion inicial al plaintext
    IPcipher_text = permute(cipher_text, IP)

#   Se aplica fk1 sobre la permutacion inicial del plain text
    preSW = apply_f_k_verbose(IPcipher_text, sk2)
    SW = preSW[4:] + preSW[:4]
    print(SW)

#   Se aplica fk2 sobre el SW obtenido y se obtiene el pre-cipher text
    preCT = apply_f_k_verbose(SW, sk1)
    print(preCT)
#   Se aplica la IP inversa, para obtener el verdadero Cipher Text
    plain_text = permute(preCT, IPINV)
    print("Plain text: ", plain_text)
    return plain_text


def verificar_tamano(cadena_binarios):
    tamano_binarios = len(cadena_binarios)
    cadena_completa = '0'*(10-tamano_binarios) + cadena_binarios
    return cadena_completa


def generar_llaves():
    lista_llaves = []
    for i in range(0, 1023):
        x = bin(i).replace("0b", "")
        llave = verificar_tamano(x)
        lista_llaves.append(llave)
    return lista_llaves


def obtener_pares_de_archivo(filename):
    lista_pares = []
    with open(filename) as file:
        for line in file:
            par = line[:-1].split(',')
            if len(par) != 2:
                print('El archivo contiene mas de dos textos por linea.')
                exit()
            if len(par[0]) != 8 or len(par[1]) != 8:
                print('El tamanio de alguno de los pares es diferente a 8.')
                exit()
            lista_pares.append(par)
    return lista_pares


def probar_llave(llave, lista_pares):
    for par in lista_pares:
        if encriptar(llave, par[0]) != par[1]:
            return False
    return True


def fuerza_bruta(filename):
    lista_pares = obtener_pares_de_archivo(filename)
    lista_llaves = generar_llaves()

    for llave in lista_llaves:
        if probar_llave(llave, lista_pares):
            return llave

    # for par in lista_pares:
    #     for llave in lista_llaves:
    #         encrypt_res = encriptar(llave, par[0])
    #         if encrypt_res == par[1]:
    #             if llave not in lista_resultados:
    #                 lista_resultados.append(llave)

    # for llave in lista_resultados:
    #     for par in lista_pares:
    #         decrypt_res = desencriptar(llave, par[1])
    #         if decrypt_res == par[0]:
    #             if lista_pares.index(par) == len(lista_pares) - 1:
    #                 return llave
    #             continue
    #         else:
    #             break


if __name__ == "__main__":

    if len(argv) > 1:
        args = argv[1:]
        file_path = args[0]
    else:
        print("""
        Uso: 
        python main.py [option] arguments
        -e          Encrypt: python main.py -e main_key plain_text
        -d          Decrypt: python main.py -d main_key cipher_text
        -b          Brute Force the key: python main.py -b filename
        -v          Verbose Procedures
        """)
        exit()

    if args[0].startswith('-'):
        if args[0].startswith('-b'):
            llave = fuerza_bruta(args[1])
            print(llave)
        elif args[0].startswith('-d'):
            main_key = args[1]
            cipher_text = args[2]
            if 'v' in args[0]:
                desencriptar_verbose(main_key, cipher_text)
            else:
                pt = desencriptar(main_key, cipher_text)
                print("Plain text: ", pt)
        elif args[0].startswith('-e'):
            main_key = args[1]
            plain_text = args[2]
            if 'v' in args[0]:
                encriptar_verbose(main_key, plain_text)
            else:
                ct = encriptar(main_key, plain_text)
                print("Cipher text: ", ct)
        else:
            print("Unknown option: ", args[0])
            exit()
    else:
        main_key = args[0]
        plain_text = args[1]
        encriptar(main_key, plain_text)

    #main_key =  '1010000010'
    #plain_text =  '10010111'
