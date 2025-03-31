/**
 * @file core.h
 * @brief Header file for core 4-bit operations, XOR, and Hamming weight.
 */
#ifndef CORE_H
#define CORE_H

#include <stddef.h> // For size_t
#include <stdbool.h> // For bool type (C99+)

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Applies a standard transformation based on a 4-bit code string.
 * Uses byte_value as the first operand and operand2 as the second for binary ops.
 * Assumes standard definitions for logic/arithmetic, 5 & 7 are NOPs.
 *
 * @param byte_value The primary input byte (0-255).
 * @param code A 4-character null-terminated string representing a binary number ("0000" to "1111").
 * @param operand2 The second operand byte (0-255) for binary operations (AND, OR, XOR, XNOR, ADD).
 * @return The transformed byte value (0-255). Returns input value on NOP or error.
 */
unsigned char apply_single_byte_transformation(unsigned char byte_value, const char* code, unsigned char operand2);

/**
 * @brief Performs byte-wise XOR between two data buffers.
 * Allocates memory for the result which must be freed by the caller using free_core_memory.
 *
 * @param data_a First data buffer.
 * @param data_b Second data buffer.
 * @param data_len Length of the buffers (must be equal).
 * @return Newly allocated buffer with XOR result (caller MUST free), or NULL on error.
 */
unsigned char* xor_datasets(const unsigned char* data_a, const unsigned char* data_b, size_t data_len);

/**
 * @brief Calculates the Hamming Weight (number of set bits) of a buffer.
 *
 * @param data Pointer to the byte buffer.
 * @param data_len Length of the buffer in bytes.
 * @return The total number of set bits (1s) in the buffer. Returns 0 if data is NULL.
 */
size_t calculate_hamming_weight(const unsigned char* data, size_t data_len);

/**
 * @brief Frees memory allocated by C functions in this library (e.g., xor_datasets).
 *
 * @param ptr Pointer to the memory to be freed (should have been allocated by malloc).
 */
void free_core_memory(void* ptr);

#ifdef __cplusplus
}
#endif

#endif // CORE_H