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
** in any way without Intel’s prior express written permission.
**
** No license under any patent, copyright, trade secret or other intellectual
** property right is granted to or conferred upon you by disclosure or delivery
** of the Materials, either expressly, by implication, inducement, estoppel or
** otherwise. Any license under such intellectual property rights must be
** express and approved by Intel in writing.
**
*/

/*
** C++ Virtual function with TM and OpenMP: TM block calls virtual fucntion 
*/

#ifndef _TM
#error TM not enabled
#endif
#ifndef _OPENMP
#error OpenMP not enabled
#endif

#include<stdio.h>
int xx = 0;

/* Base class for C++ Transactional Memory virtual function example */
class BaseXXX 
{
   public:
__attribute__((tm_callable))
   virtual void TxnAddOne() 
   {
     xx = xx + 1;
#ifdef DEBUG 
     printf("Transactional Memory Base class: virtual function \n");
#endif
   }
};

/* Virtual class for C++ Transactional Memory virtual function example */
class VirtualYYY : public BaseXXX
{
  public:
    __attribute__((tm_callable))
    void TxnAddOne()
    {
      xx = xx + 1;
#ifdef DEBUG 
      printf("Transactional Memory Virtual class: function \n");
#endif
    }
};

int main()
{
  BaseXXX *x, *y;
   
#pragma omp parallel sections num_threads(2)
  {
    __tm_atomic {
      x = new BaseXXX();
      x->TxnAddOne();
    }
#pragma omp section
    __tm_atomic {
      y = new VirtualYYY();
      y->TxnAddOne();
    }
  }

  if (xx==2) {
    printf("passed\n");
  }
  else {
    printf("failed\n");
  }
}


