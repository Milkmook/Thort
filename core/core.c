/**
 * @file core.c
 * @brief Implementation of core 4-bit operations, XOR, and Hamming weight.
 */
#include "core.h"
#include <stdlib.h>  // For malloc, free
#include <string.h>  // For strlen
#include <stdio.h>   // For perror (optional error reporting)
// #define CORE_DEBUG // Uncomment for debug prints in code_to_op

// --- Function Table (Internal Mapping) ---
// Defines the operation associated with each 4-bit code.
typedef enum {
    OP_NOP, OP_INC, OP_XNOR, OP_SHL, OP_AND, OP_SHR,
    OP_DEC, OP_ROL, OP_ROR, OP_ADD, OP_OR, OP_XOR, OP_NOT
} OperationType;

// Convert 4-char binary string code to OperationType enum
// Returns OP_NOP for invalid codes.
static OperationType code_to_op(const char* code) {
    if (!code || strlen(code) != 4) return OP_NOP;
    // Simple binary string to integer conversion
    int val = 0;
    for(int i = 0; i < 4; ++i) {
        if (code[i] == '1') {
            val |= (1 << (3 - i));
        } else if (code[i] != '0') {
            // Invalid character in code string
            #ifdef CORE_DEBUG // Optional debug prints
            fprintf(stderr, "Warning: Invalid character '%c' in code '%s'\n", code[i], code);
            #endif
            return OP_NOP;
        }
    }

    // Based on final confirmed function table (5 and 7 are NOPs)
    switch (val) {
        case 0: return OP_NOP;  // 0000
        case 1: return OP_INC;  // 0001
        case 2: return OP_XNOR; // 0010
        case 3: return OP_SHL;  // 0011
        case 4: return OP_AND;  // 0100
        case 5: return OP_NOP;  // 0101 (Explicit NOP)
        case 6: return OP_SHR;  // 0110
        case 7: return OP_NOP;  // 0111 (Explicit NOP)
        case 8: return OP_DEC;  // 1000
        case 9: return OP_ROL;  // 1001
        case 10: return OP_ROR; // 1010
        case 11: return OP_ADD; // 1011
        case 12: return OP_OR;  // 1100
        case 13: return OP_XOR; // 1101
        case 14: return OP_DEC; // 1110 (Also DEC)
        case 15: return OP_NOT; // 1111
        default: return OP_NOP; // Should not happen with 4 bits
    }
}

// --- Public API Implementation ---

/**
 * @brief Applies a standard transformation based on a 4-bit code string.
 * Uses byte_value as the first operand and operand2 as the second for binary ops.
 */
unsigned char apply_single_byte_transformation(unsigned char byte_value, const char* code, unsigned char operand2) {
    OperationType op = code_to_op(code);
    unsigned char val = byte_value;
    unsigned char op2 = operand2;

    switch (op) {
        case OP_NOP: break; // Includes 0, 5, 7
        case OP_INC: val++; break;
        case OP_XNOR: val = ~(val ^ op2); break; // Standard XNOR
        case OP_SHL: val <<= 1; break; // Standard Shift Left (Logical)
        case OP_AND: val &= op2; break; // Standard AND
        case OP_SHR: val >>= 1; break; // Standard Shift Right (Logical)
        case OP_DEC: val--; break; // Standard Decrement (for 8, E)
        case OP_ROL: { // Rotate Left
            unsigned char msb = (val & 0x80) ? 1 : 0;
            val = (val << 1) | msb;
            break;
        }
        case OP_ROR: { // Rotate Right
            unsigned char lsb = (val & 0x01) ? 1 : 0;
            val = (val >> 1) | (lsb << 7);
            break;
        }
        case OP_ADD: val += op2; break; // Standard ADD (wraps)
        case OP_OR: val |= op2; break; // Standard OR
        case OP_XOR: val ^= op2; break; // Standard XOR
        case OP_NOT: val = ~val; break; // Standard NOT
    }
    return val;
}

/**
 * @brief Performs byte-wise XOR between two data buffers.
 * Allocates memory for the result which must be freed by the caller using free_core_memory.
 */
unsigned char* xor_datasets(const unsigned char* data_a, const unsigned char* data_b, size_t data_len) {
    if (!data_a || !data_b || data_len == 0) {
         #ifdef CORE_DEBUG
         fprintf(stderr, "Error: Invalid args to xor_datasets\n");
         #endif
         return NULL;
    }
    unsigned char* result = (unsigned char*)malloc(data_len);
    if (!result) {
        perror("malloc failed in xor_datasets");
        return NULL;
    }
    for (size_t i = 0; i < data_len; ++i) {
        result[i] = data_a[i] ^ data_b[i];
    }
    return result;
}

/**
 * @brief Calculates the Hamming Weight (number of set bits) of a buffer.
 */
size_t calculate_hamming_weight(const unsigned char* data, size_t data_len) {
    if (!data) return 0;
    size_t total_weight = 0;
    for (size_t i = 0; i < data_len; ++i) {
        unsigned char byte = data[i];
        unsigned char weight = 0;
        while (byte > 0) {
            byte &= (byte - 1); // Brian Kernighan's algorithm
            weight++;
        }
        total_weight += weight;
    }
    return total_weight;
}

/**
 * @brief Frees memory allocated by C functions in this library (e.g., xor_datasets).
 */
void free_core_memory(void* ptr) {
    if (ptr) {
        free(ptr);
    }
}