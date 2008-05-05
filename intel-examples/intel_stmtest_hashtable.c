/*
** Copyright 2007 Intel Corporation All Rights Reserved.
**
** The source code contained or described herein and all documents related to
** the source code ("Material") are owned by Intel Corporation or its suppliers
** or licensors. Title to the Material remains with Intel Corporation or its
** suppliers and licensors. The Material contains trade secrets and proprietary
** and confidential information of Intel or its suppliers and licensors. The
** Material is protected by worldwide copyright and trade secret laws and treaty
** provisions. No part of the Material may be used, copied, reproduced,
** modified, published, uploaded, posted, transmitted, distributed, or disclosed
** in any way without IntelÎéÎ÷s prior express written permission.
**
** No license under any patent, copyright, trade secret or other intellectual
** property right is granted to or conferred upon you by disclosure or delivery
** of the Materials, either expressly, by implication, inducement, estoppel or
** otherwise. Any license under such intellectual property rights must be
** express and approved by Intel in writing.
**
*/

/*
** A simple hashtable with binary tree buckets.  TM is used to protect accesses
** to each bucket. 
*/

#if defined(_WIN32)
#define _CRT_SECURE_NO_DEPRECATE
#endif

#if defined(_OPENMP)
#include <omp.h>
//A more scalable malloc/free
#define malloc kmp_malloc
#define free kmp_free
#else
#include <malloc.h>
#endif

#include <stdio.h>
#include <time.h>
#include <stdlib.h>
#include <string.h>

/* Ensure no warnings when compiling without OpenMP, by macro-ing away the pragmas */
#if defined (_OPENMP)
#define Pragma(args) _Pragma (#args)
# define ATOMIC Pragma(omp atomic)
# define PARALLEL_FOR_SHARED(...) Pragma(omp parallel for shared (__VA_ARGS__))
#else
# define ATOMIC
# define PARALLEL_FOR_SHARED(...) 
#endif

#if defined(_TM)
# define SYNC_BEGIN(lock) __tm_atomic {
# define SYNC_END(lock) }
# define INIT_SYNC(lock) (void)0
# define TM_CALLABLE __declspec(tm_callable)
# define DECLARE_SYNC(lock) 
#else
/* Being compiled without TM */
# define TM_CALLABLE
# if defined(_OPENMP)
#  define SYNC_BEGIN(lock) omp_set_lock(&lock)
#  define SYNC_END(lock) omp_unset_lock(&lock) 
#  define INIT_SYNC(lock) omp_init_lock(&lock) 
#  define DECLARE_SYNC(lock) omp_lock_t lock; 
# else
//We have no parallelism so we don't need synchronization
#  define SYNC_BEGIN(lock) 
#  define SYNC_END(lock) 
#  define INIT_SYNC(lock) (void)0
#  define DECLARE_SYNC(lock) 
# endif
#endif

enum {searching, success, failure, error};

typedef struct btree_node btree_t;

struct btree_node {
    int value;
    btree_t * left;
    btree_t * right;
    btree_t * parent;
}; 

typedef struct hashbucket {
    DECLARE_SYNC(lock)
    btree_t * tree;
} hashbucket_t;

typedef struct hashtable {
    int size;
    hashbucket_t * buckets;
    int add;
    int remove;
    int add_success; 
    int remove_success; 
}hashtable_t;

btree_t * create_new_node(int value)
{
    btree_t * node = (btree_t *)malloc(sizeof(btree_t));
    if (node == NULL)
    {
        return NULL;
    }

    node->value = value;
    node->left = NULL;
    node->right = NULL;
    node->parent = NULL;

    return node;
}

TM_CALLABLE 
int add_to_tree(btree_t **head, btree_t * node)
{
    int ret_val = failure;
    if (*head == NULL)
    {
        *head = node;
        ret_val = success;
    }
    else
    {
        btree_t * current = *head;
        for (;;)
        {
            if (node->value < current->value)
            {
                if (current->left == NULL)
                {
                    current->left = node;
                    node->parent = current;
                    ret_val = success;
                    break;
                }
                else
                {
                    current = current->left;
                }
            }
            else if (node->value > current->value)
            {
                if (current->right == NULL)
                {
                    current->right = node;
                    node->parent = current;
                    ret_val = success;
                    break;
                }
                else {
                    current = current->right;
                }
            }
            else {
                break;
            }
        }
    }
    return ret_val;
}

/* replace the head of a subtree */
TM_CALLABLE 
btree_t * replace_head(btree_t * head)
{
    btree_t * replacement = head;
    if (head->left == NULL) {
        replacement = head->right;
    }
    else if (head->right == NULL){
        replacement = head->left;
    }
    else
    {
        replacement = head->left;
        while (replacement->right != NULL)
            replacement = replacement->right;

        replacement->right = head->right;
        if (head->right != NULL)
            head->right->parent = replacement;

        if (head->left != replacement)
        {
            replacement->parent->right = replacement->left;
            if (replacement->left) 
                replacement->left->parent = replacement->parent;
            replacement->left = head->left;
            if (head->left != NULL) 
                head->left->parent = replacement;
        }
    }
    if (replacement != NULL)
    {
        replacement->parent = head->parent;
    }
    return replacement;
}

TM_CALLABLE 
btree_t * remove_from_tree(btree_t **head, int value)
{
    btree_t * ret_val = NULL;
    if (*head != NULL)
    {
        btree_t * current = *head;
        for (;;)
        {
            if (value < current->value)
            {
                if (current->left == NULL)
                {
                    break;
                }
                else 
                {
                    current = current->left;
                }
            }
            else if (value > current->value)
            {
                if (current->right == NULL)
                {
                    break;
                }
                else 
                {
                    current = current->right;
                }
            }
            else {
                btree_t * parent = current->parent;
                btree_t * replacement = replace_head(current);
                if (parent == NULL){
                    *head = replacement;
                }
                else
                {
                    if (parent->left == current) 
                    { 
                        parent->left = replacement;
                    }
                    else if (parent->right == current){

                        parent->right = replacement;
                    }
                }
                ret_val = current;
                break;
            }
        }
    }
    return ret_val;
}

void traverse_tree(btree_t * head, int level)
{
    char format_string[256];
    if (head == NULL) return;
    if (head->left != NULL) traverse_tree(head->left, level + 1);

    sprintf(format_string, " %%-%is value %%i %%p parent %%i\n", level);
    printf(format_string, "", head->value, head, head->parent? head->parent->value: -1);

    if (head->right != NULL) traverse_tree(head->right, level + 1);

}
void traverse_hashtable(hashtable_t * table)
{
    int i;
    for (i=0; i<table->size; i++)
    {
        printf("\nbucket %i\n", i);
        traverse_tree(table->buckets[i].tree, 0);
    }
}

int add_to_hashtable(hashtable_t *table, int value)
{
    hashbucket_t * bucket = &table->buckets[value % table->size];
    btree_t * node;
    int ret_val;
    ATOMIC    
    table->add++;
    //We don't presently support transactional malloc so we should 
    //preallocate to avoid wasting memory.
    if ((node = create_new_node(value)) == NULL) return error;

    SYNC_BEGIN(bucket->lock);
    ret_val = add_to_tree(&bucket->tree, node);
    SYNC_END(bucket->lock);

    if (ret_val == failure)
    {
        return failure;
    }
    else
    {
        ATOMIC
        table->add_success++;
    }
    return success;
}

int remove_from_hashtable(hashtable_t *table, int value)
{
    hashbucket_t * bucket = &table->buckets[value % table->size];
    btree_t * node;

    ATOMIC
    table->remove++;
   
    SYNC_BEGIN(bucket->lock);
    node = remove_from_tree(&bucket->tree, value);
    SYNC_END(bucket->lock);

    if (node) {
        ATOMIC
        table->remove_success++;
        free(node);
        return success;
    }
    return failure;
}

void usage(char * exe)
{
    printf("Usage: %s [<size of hashtable> [<number of items> [<number of duplicates>]]]\n", exe);
    exit(-1); 
}

int main(int argc, char ** argv)
{
    hashtable_t table;
    int i;
    int * items;
    int num_items = 1000000;
    int duplicates = 10000;
    clock_t start, end;
    table.size = 229;

    if (argc > 1) {
        switch (argc) {
            case 4:
                duplicates = atoi(argv[3]);
            case 3:
                num_items = atoi(argv[2]);
            case 2:
                table.size = atoi(argv[1]);
                if (duplicates < 0 || num_items <=0 || table.size <=0 || duplicates > num_items/2)
                    usage(argv[0]);
                break;
            default:
                usage(argv[0]);
        }
    }

    printf("Running with these parameters:\n");
    printf("  Size of hashtable:      %d\n", table.size);
    printf("  Number of items:        %d\n", num_items);
    printf("  Number of duplicates:   %d\n\n", duplicates);

    items = (int *)malloc(sizeof(int)*num_items);

    table.add = table.remove = table.add_success = table.remove_success = 0;
    table.buckets = (hashbucket_t *)malloc(sizeof(hashbucket_t)*table.size);
    memset(table.buckets, 0, sizeof(hashbucket_t)*table.size);
    for (i=0; i<table.size; i++)
        INIT_SYNC(table.buckets[i].lock);

    for (i=0; i<num_items-duplicates; i++)
    {
        items[i] = i + 1; 
    }

    /* some duplicate entries */
    for (i=num_items-duplicates; i<num_items; i++)
    {
        items[i] = i - (num_items - duplicates) + 1; 
    }

    //We want predictable results so use the same seed every time 
    srand(0xdeadbeef); 
    /* shuffle the array */
    for (i=0; i<num_items; i++)
    {
        unsigned int number; 
        int index;
        int value;
        //Adding the index is an attemp to cover more values than can be supported by RAND_MAX
        index = ((int)((double)num_items*rand()/((double)RAND_MAX)) + i) % num_items;

        value = items[i];
        items[i] = items[index];
        items[index] = value; 
    }

    printf("Running add test\n");
    start = clock();

    PARALLEL_FOR_SHARED(table, items, num_items)
    for (i=0; i<num_items; i++)
    {
        add_to_hashtable(&table, items[i]);
    }
    end = clock();
    printf("Elapsed %6.2lf seconds\n\n", (double)(end - start)/CLOCKS_PER_SEC);
    
    start = clock();
    printf("Running remove test\n");

    PARALLEL_FOR_SHARED(table, items, num_items)
    for (i=0; i<num_items; i++)
    {
        remove_from_hashtable(&table, items[i]);
    }
    end = clock();
    printf("Elapsed %6.2lf seconds\n\n", (double)(end - start)/CLOCKS_PER_SEC);

    printf("add attempts:     %i\n", table.add);
    printf("add successes:    %i\n", table.add_success);
    printf("remove attempts:  %i\n", table.remove);
    printf("remove successes: %i\n", table.remove_success);

    if (table.add_success == (num_items - duplicates) && 
            table.remove_success == (num_items - duplicates))
        printf("Test passed\n");
    else
        printf("Test failed\n");
}
