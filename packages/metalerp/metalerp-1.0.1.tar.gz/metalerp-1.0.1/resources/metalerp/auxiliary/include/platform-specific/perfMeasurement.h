    // efficient performance measurement utilities
    // The global variables that are used in this lib are not multi-threading safe, you can easily get erroneous results when measuring closely performing functions separately in multiple threads.
    //but it is wiser to not make them threading-safe (and instead always measure in a single thread) with locking because that would distort the measurement even more with lock acquisition/release overhead.


    #if !defined(PERF_M_H) && !defined(LIB_METALERP)
    #define PERF_M_H
    
    #ifndef METALERP_FAST
    #define METALERP_FAST
    #endif
    #define METALERP_DEVELOPMENT
    #define INCLUDE_METALERP_INTERNAL_MACRO_UTILS
    #include "../../../core/include/metalerpDefs.h"
    #include "../../../core/include/headers/external/xoshiro256plus.h"
    #include "../../../core/include/headers/external/xoshiro256plusplus.h"
    
    #ifdef METALERP_VOTES_MAX
        #undef METALERP_VOTES_MAX
        #undef METALERP_AVERAGING_SIZE
        #define METALERP_VOTES_MAX 9
        #define METALERP_AVERAGING_SIZE 7
    #endif


    //utils

    #define ALLOCATE_IN_OUT(count) \
        type* in##count = malloc(sizeof(type)*count);   \
        type* out##count = malloc(sizeof(type)*count); \
        fillArr_RandomF(in##count, count, 0);

    #define SCALAR_VS_Measurement(count, function1, function2) determineFasterScalar(in##count, out##count, cast(size_t, count), cast(scalarTransform, function1), cast(scalarTransform, function2), #function1, #function2)

    #define BATCHED_VS_Measurement(count, function1, function2) determineFasterBatch(in##count, out##count, cast(size_t, count), cast(batchTransform, function1), cast(batchTransform, function2), #function1, #function2)


    #define RE_SCRAMBLE_IN_OUT(count) fillArr_RandomF(in##count, count, 0); /*
    the perf measurement functions of metalerp randomize arrays and automatically do Dcache-heating themselves
    so there's no need for this when only metalerp's perf measurement utilities are used*/

    #define FREE_IN_OUT(count) free(in##count); in##count = NULL; free(out##count); out##count = NULL;

    #define REUSE_IN_OUT(count) if(in##count && out##count) {FREE_IN_OUT(count)} if(!in##count) { in##count = malloc(sizeof(type)*count); fillArr_RandomF(in##count, count, 0); } if(!out##count) { out##count = malloc(sizeof(type)*count); }


    METALERP_HEURISTICS_VARIABLES
    static double ELAPSED;

    //randomizers (good statistical properties, from xoshiro256+)
    STATIC_FORCE_INLINE float posrandF() //+[0, 1]
    {
        return cast(float, nextF());
    }

    STATIC_FORCE_INLINE float negrandF() //-[0, 1]
    {
        return cast(float, -nextF());
    }

    STATIC_FORCE_INLINE float mixedrandF() //±[0, 1] - branchless but heavy arithmetic
    {
        int64_t sign = (((int64_t)(next()>>63))&((int64_t)1));
        float r = nextF();
        return  (sign) * r - (!sign) * r;
    }

    static const float iMaxOffsetted = ((float)INT_MAX)+1.f;
    STATIC_FORCE_INLINE float mixedrandF2() //±[0, 1] - only 1 next call to generate a 32-bit signed int and normalize by signed integer maximum
    {
        return ((float)(((int64_t)next())>>32))/(iMaxOffsetted); //uses plusplus's better uint64 randomization
    }

    STATIC_FORCE_INLINE void DcacheWarmer(type* restrict in, type* restrict out, size_t length)
    {
        for(int64_t i = (int64_t)length-1; i>=0; --i)
        { 
            in[i] = mixedrandF2();
            
            out[i] = 0;

        }

        for(size_t i = 0; i<length; ++i)
        {    
            out[i] = in[i] + mixedrandF2();
        }
    }
    //type must be fp or else the array gets filled with zeros
    void fillArr_RandomF(type* array, size_t len,  char inputTypeFlag)
    {
        selfSeedPlus();
        selfSeed();
        if(inputTypeFlag<0)
        for(size_t i=0; i<len; ++i)
            array[i] = negrandF();

        else if(inputTypeFlag==0)
        for(size_t i=0; i<len; ++i)
            array[i] = mixedrandF2();
        
        else
        for(size_t i=0; i<len; ++i)
            array[i] = posrandF();
    }


    typedef type(*scalarTransform)(type);
    void determineFasterScalar(type* restrict in, type* restrict out, size_t length, scalarTransform fn1, scalarTransform fn2, const char* fn1Name, const char* fn2Name)
    {   
        METALERP_HEURISTICS_VARIABLES double ELAPSED_F1, ELAPSED_F2;
        
        for(int64_t i = length-1; i>=0; --i)
        { 
            in[i] = mixedrandF2();
            
            out[i] = 0;

        }

        for(size_t i = 0; i<length; ++i)
        {    
            out[i] = in[i] + mixedrandF2();
        }
        
        SLEEP(1);

        int votes = 0;
        double F1ElapsedSum = 0, F2ElapsedSum = 0;
        for(int n = 1; n<=METALERP_VOTES_MAX; ++n)
        {
            ELAPSED_F1 = 0;
            ELAPSED_F2 = 0;
            for(size_t a = 0; a < cast(size_t, METALERP_AVERAGING_SIZE); ++a)
            {
                GET_FREQ(&FREQUENCY);
                MEASURE(&START);
                for(size_t i = 0; i<length; ++i)
                {
                    out[i] = fn1(in[i]);
                }
                MEASURE(&END);
                ELAPSED_F1 += calcElapsed(FREQUENCY, START, END);
                SLEEP(1);
                //----------------------------------------
                GET_FREQ(&FREQUENCY);
                MEASURE(&START);
                for(size_t i = 0; i<length; ++i)
                {
                    out[i] = fn2(in[i]);
                }
                MEASURE(&END);
                ELAPSED_F2 += calcElapsed(FREQUENCY, START, END);
                SLEEP(1);

            }
            
            ELAPSED_F1 = ELAPSED_F1/cast(double, METALERP_AVERAGING_SIZE);
            ELAPSED_F2 = ELAPSED_F2/cast(double, METALERP_AVERAGING_SIZE);
            
            F1ElapsedSum += ELAPSED_F1; F2ElapsedSum += ELAPSED_F2;

        // printf("Fn1: %.5f, Fn2: %.5f\n", ELAPSED_F1*1000.0, ELAPSED_F2*1000.0);
            ELAPSED_F1 < ELAPSED_F2 ? ++votes : --votes;

            int diff = METALERP_VOTES_MAX - n;

            if( abs(votes) > diff )
                break;

        }
        
        F1ElapsedSum /= cast(double, METALERP_VOTES_MAX);
        F2ElapsedSum /= cast(double, METALERP_VOTES_MAX);

        printf("\n\n[%s] vs [%s] scalar single-threaded execution results: \n------------------\n", fn1Name, fn2Name);
        if(F1ElapsedSum <= F2ElapsedSum) //absolute difference works too but I'm not too bothered to refactor this stupidity
        {
            double diff = (F2ElapsedSum - F1ElapsedSum);
            printf("[%s] was faster by %.7f (ms) on average (total exec time)\nand %.5f (ns) faster on average (single-execution)\n", fn1Name, diff * 1000.0, cast(double, (diff * cast(double, 1e+9)) / length));
        }
        else
        {
            double diff = (F1ElapsedSum - F2ElapsedSum);
            printf("[%s] was faster by %.7f (ms) on average (total exec time)\nand %.5f (ns) faster on average (single-execution)\n", fn2Name,  diff * 1000.0, cast(double, (diff * cast(double, 1e+9)) / length));
        }
    }

    typedef void(*batchTransform)(type* restrict in, type* restrict out, const size_t length);

    void determineFasterBatch(type* restrict in, type* restrict out, size_t length, batchTransform fn1, batchTransform fn2, const char* fn1Name, const char* fn2Name)
    {   
        METALERP_HEURISTICS_VARIABLES double ELAPSED_F1, ELAPSED_F2;


        for(int64_t i = length-1; i>=0; --i)
        { 
            in[i] = mixedrandF2();
            
            out[i] = 0;
        }

        for(size_t i = 0; i<length; ++i)
        {    
            out[i] = in[i] + mixedrandF2();
        }
        
        SLEEP(1);

        int votes = 0;
        double F1ElapsedSum = 0, F2ElapsedSum = 0;
        for(int n = 1; n<=METALERP_VOTES_MAX; ++n)
        {
            ELAPSED_F1 = 0;
            ELAPSED_F2 = 0;
            for(size_t a = 0; a < cast(size_t, METALERP_AVERAGING_SIZE); ++a)
            {
                GET_FREQ(&FREQUENCY);
                MEASURE(&START);
                fn1(in, out, length);
                MEASURE(&END);
                ELAPSED_F1 += calcElapsed(FREQUENCY, START, END);
                SLEEP(1);
                //----------------------------------------
                GET_FREQ(&FREQUENCY);
                MEASURE(&START);
                fn2(in, out, length);
                MEASURE(&END);
                ELAPSED_F2 += calcElapsed(FREQUENCY, START, END);
                SLEEP(1);

            }
            
            ELAPSED_F1 = ELAPSED_F1/cast(double, METALERP_AVERAGING_SIZE);
            ELAPSED_F2 = ELAPSED_F2/cast(double, METALERP_AVERAGING_SIZE);
            
            F1ElapsedSum += ELAPSED_F1; F2ElapsedSum += ELAPSED_F2;

        // printf("Fn1: %.5f, Fn2: %.5f\n", ELAPSED_F1*1000.0, ELAPSED_F2*1000.0);
            ELAPSED_F1 < ELAPSED_F2 ? ++votes : --votes;

            int diff = METALERP_VOTES_MAX - n;

            if( abs(votes) > diff )
                break;

        }
        
        F1ElapsedSum /= cast(double, METALERP_VOTES_MAX);
        F2ElapsedSum /= cast(double, METALERP_VOTES_MAX);

        printf("\n\n[%s] vs [%s] Batched execution results: \n------------------\n", fn1Name, fn2Name);

        if(F1ElapsedSum <= F2ElapsedSum) 
        {
            double diff = (F2ElapsedSum - F1ElapsedSum) * 1000.0;
            printf("[%s] was faster by %.7f (ms) on average (total exec time)\nand %.5f (ns) faster on average (single-execution)\n", fn1Name, diff, cast(double, (diff * cast(double, 1e+3)) / length));
        }
        else
        {
            double diff = (F1ElapsedSum - F2ElapsedSum) * 1000.0;
            printf("[%s] was faster by %.7f (ms) on average (total exec time)\nand %.5f (ns) faster on average (single-execution)\n", fn2Name, diff, cast(double, (diff * cast(double, 1e+3)) / length));
        }
    }


    int unsigned logger = 1;

    #define printElapsed(functionName) printf("\n-----------------\nmeasurement no. %d - (%s)\n-----------------\nelapsed (ms): %.6f\n-----------------\nelapsed (s): %.10f\n", logger, #functionName, (ELAPSED*1000.0), ELAPSED)  

    #define queryPerf(function, ...)  \
                \
        MEASURE(&START);                \
        function(__VA_ARGS__);                          \
        MEASURE(&END);                  \
                                                        \
        ELAPSED = calcElapsed(FREQUENCY, START, END);   \
                                                        \
        printElapsed(ELAPSED, function);                          \
        logger += 1;

        
    #define noDBG_qPerf(outVar,  function, ...)  \
            \
        MEASURE(&START);                \
        outVar function(__VA_ARGS__);                          \
        MEASURE(&END);                  \
        ELAPSED = calcElapsed(FREQUENCY, START, END);
        
    #define WARMUP(iterations, outVar, func, ...)    \
        for(size_t i = 0; i < iterations; ++i)    \
        {                   \
            type val = func(__VA_ARGS__);\
            outVar += val;       \
        }

    #define WARMUPNonNative(iterations, func, ...)    \
        for(size_t i = 0; i < iterations; ++i)    \
        {                           \
            func(__VA_ARGS__);       \
        }              

    volatile double totalT = 0.0;
    volatile double perfSums = 0.0;
    volatile double trickSum = 0.0;
    /*it'll just have to be a specific solution for now with only functions that return floats or doubles.*/

    // cache heat cooling (to not distort perf measurements with previous ones' execution ~ OS is allowed half a second to scramble caches enough after each perf-measurement's run, sleeps are done in this kind of dependency-rich block to ensure the compiler never optimizes it away)
    #define trickSleep()  \
        GET_FREQ(&FREQUENCY);    \
        MEASURE(&START); SLEEP(500); MEASURE(&END);                                 \
        ELAPSED = calcElapsed(FREQUENCY, START, END);             \
        printf("\ntrick-sleep (cache cooler) executed for: %.6f (ms)\n", ELAPSED*1000.0); /*check it executed*/
        
    /*SCALAR PERF MEASURERS*/
    #define averagePerfDynamicInput(iterations, function)   \
        do { type /*just stupid mangling before deciding to make the expansions of these macros scoped with do{}while();*/ y##function##_DI = 0.0;                       \
        WARMUP(1000, y##function##_DI, function, cast(type, mixedrandF2()))    /*I-cache-heating, test when the kernel is already well-cached after 1k calls*/ \
        perfSums = 0.0;  totalT = 0.0;   printf("\n**************************************************\n%s\n", #function);  GET_FREQ(&FREQUENCY);    \
        trickSum = 0.0;                            \
        for(size_t i=0; i<iterations; ++i)                              \
            {   type x##function = cast(type, mixedrandF2());                                                     \
                noDBG_qPerf(y##function##_DI = , function, x##function) \
                perfSums += (double)ELAPSED;   if(!(i%(iterations/3))) { /*printf("iteration (%d)\nchecking input x for this iteration: %f\n", (i+1), x##function); */ SLEEP(1); /*sleep or we'll be doing proper crypto-mining*/  }                                   \
                trickSum += (double)y##function##_DI;    \
            }   \
        totalT = perfSums;  \
        perfSums /= ((double)iterations);                                     \
        printf("\n-------------------\nCall-> %s(MIXED RANDOM INPUT);\n\n(TOTAL TIME) ** %d iterations **:\n->%.6f (ms)\n->%.12f (s)\n\n(average SINGLE CALL exec time):\n->%.6f (ms)\n->%.4f (nanosec)\ntotal trickSum: %f\n", #function, iterations, totalT*1000.0, totalT, perfSums*1000.0, perfSums*1000000000.0, trickSum);  \
        trickSleep() } while(0); /*a little break for the thread running measurements especially if these averagePerf funcs are called many times sequentially for same/different funcs in case many functions' instructions affect the performance of each other (due to arithmetic instruction similarities)*/ 

    #define averagePerfDynamicInputNegative(iterations, function)   \
        do {type y##function##_DI##N = 0.0;                        \
        WARMUP(1000, y##function##_DI##N, function, cast(type, negrandF()))     \
        perfSums = 0.0;  totalT = 0.0;   printf("\n**************************************************\n%s\n", #function);  GET_FREQ(&FREQUENCY);    \
        trickSum = 0.0;                            \
        for(size_t i=0; i<iterations; ++i)                              \
            {   type x##function = cast(type, negrandF());                                                         \
                noDBG_qPerf(y##function##_DI##N = , function, x##function) \
                perfSums += (double)ELAPSED;   if(!(i%(iterations/3))) { /*printf("iteration (%d)\nchecking input x for this iteration: %f\n", (i+1), x##function);*/  SLEEP(1);  }                                   \
                trickSum += (double)y##function##_DI##N;    \
            }   \
        totalT = perfSums;  \
        perfSums /= ((double)iterations);                                     \
        printf("\n-------------------\nCall-> %s(STRICTLY NEGATIVE RANDOM INPUT);\n\n(TOTAL TIME) ** %d iterations **:\n->%.6f (ms)\n->%.12f (s)\n\n(average SINGLE CALL exec time):\n->%.6f (ms)\n->%.4f (nanoSec)\ntotal trickSum: %f\n", #function, iterations, totalT*1000.0, totalT, perfSums*1000.0, perfSums*1000000000.0, trickSum); \
        trickSleep()} while(0);

    #define averagePerfDynamicInputPositive(iterations, function)   \
        do {type y##function##_DI##P = 0.0;                        \
        WARMUP(1000, y##function##_DI##P, function, cast(type, posrandF()))     \
        perfSums = 0.0;  totalT = 0.0;   printf("\n**************************************************\n%s\n", #function);  GET_FREQ(&FREQUENCY);    \
        trickSum = 0.0;                            \
        for(size_t i=0; i<iterations; ++i)                              \
            {   type x##function = cast(type, posrandF());                                                         \
                noDBG_qPerf(y##function##_DI##P = , function, x##function) \
                perfSums += (double)ELAPSED;   if(!(i%(iterations/3))) { /*printf("iteration (%d)\nchecking input x for this iteration: %f\n", (i+1), x##function);*/  SLEEP(1);  }                                   \
                trickSum += (double)y##function##_DI##P;    \
            }   \
        totalT = perfSums;  \
        perfSums /= ((double)iterations);                                     \
        printf("\n-------------------\nCall-> %s(STRICTLY POSITIVE RANDOM INPUT);\n\n(TOTAL TIME) ** %d iterations **:\n->%.6f (ms)\n->%.12f (s)\n\n(average SINGLE CALL exec time):\n->%.6f (ms)\n->%.4f (nanoSec)\ntotal trickSum: %f\n", #function, iterations, totalT*1000.0, totalT, perfSums*1000.0, perfSums*1000000000.0, trickSum); \
        trickSleep()} while(0);

    #define averagePerfDynamicInput_2Inputs(iterations, function)   \
        do {type y##function##_DI = 0.0;                        \
        WARMUP(1000, y##function##_DI, function, cast(type, mixedrandF2()), cast(type, mixedrandF2())) /*default warm up loop count = 30*/     \
        perfSums = 0.0;  totalT = 0.0;   printf("\n**************************************************\n%s\n", #function);  GET_FREQ(&FREQUENCY);    \
        trickSum = 0.0;                            \
        for(size_t i=0; i<iterations; ++i)                              \
            {   type x##function = (type)mixedrandF2(),    \
                x2##function = (type)mixedrandF2();                                                        \
                noDBG_qPerf(y##function##_DI = , function, x##function, x2##function) \
                perfSums += (double)ELAPSED;  if(!(i%(iterations/3))) {  /*printf("iteration (%d)\nchecking input x for this iteration: %f\ninput x2 for this iteration: %f\n", (i+1), x##function, x2##function); */ SLEEP(1);   }                                   \
                trickSum += (double)y##function##_DI;    \
            }   \
        totalT = perfSums;  \
        perfSums /= ((double)iterations);                                     \
        printf("\n-------------------\nCall-> %s(RANDOM INPUT1, RANDOM INPUT2);\n\n(TOTAL TIME) ** %d iterations **:\n->%.6f (ms)\n->%.12f (s)\n\n(average SINGLE CALL exec time):\n->%.6f (ms)\n->%.4f (nanoSec)\ntotal trickSum: %f\n", #function, iterations, totalT*1000.0, totalT, perfSums*1000.0, perfSums*1000000000.0, trickSum);\
        trickSleep()} while(0);


    #define averagePerfNonNative(iterations, function, ...)  /*measures any function that isn't natively implemented as a part of the lib, doesn't assume it returns values*/ \
                            \
        do {WARMUPNonNative(30, function, __VA_ARGS__)   /*may prove useful for any func that needs any sort input argument list of arbitrary size.*/  \
        perfSums = 0.0;  totalT = 0.0;   printf("\n**************************************************\n%s\n", #function);  GET_FREQ(&FREQUENCY);    \
                                    \
        for(size_t i=0; i<iterations; ++i)                              \
            {                                                                \
                noDBG_qPerf( , function, __VA_ARGS__) \
                perfSums += (double)ELAPSED;  if(!(i%(iterations/2))) {/*  printf("iteration (%d)\n", (i+1)); */ SLEEP(1);}                           \
                    \
            }   \
        totalT = perfSums;  \
        perfSums /= ((double)iterations);                                     \
        printf("\n-------------------\nCall-> %s(%s);\n\n(TOTAL TIME) ** %d iterations **:\n->%.6f (ms)\n->%.12f (s)\n\n(average SINGLE CALL exec time):\n->%.6f (ms)\n->%.4f (nanoSec)\n", #function, #__VA_ARGS__, iterations, totalT*1000.0, totalT, perfSums*1000.0, perfSums*1000000000.0);\
        trickSleep()} while(0);

    //these could REALLY fill up memory with a large enough array length, resource request might even not get accepted by OS or process might get killed
    static inline void heatUpPages(type* restrict in, type* restrict out, size_t len)
    {
        for(int64_t i = len; i>=0; --i)
        {
            in[i] = out[i] * nextF(); //changes that don't affect sign of the number
        }
        for(size_t i = 0; i<len; ++i)
        {
            out[i] = in[i] * nextF(); //same here
        }
    }
    #define VEC_averagePerfDynamicInput(arr_len, function)   \
        do {type* y##function##_DI_VEC = malloc(sizeof(type)*arr_len), *y##function##_DO_VEC = malloc(arr_len * sizeof(type));                      \
        type warmUpArrIN##function##DI[1000] = {0}, warmUpArrOUT##function##DI[1000] = {0}; \
        fillArr_RandomF(warmUpArrIN##function##DI, 1000, 0);                                          \
        fillArr_RandomF(y##function##_DI_VEC, arr_len, 0); /*0 to fill with mixed-sign rands, 1 to fill with positive rands, -1 to fill with negatives*/                                                    \
        function(warmUpArrIN##function##DI, warmUpArrOUT##function##DI, 1000); /*warmup of the vectorized versions*/\
        perfSums = 0.0;  totalT = 0.0;   printf("\n**************************************************\n%s\n", #function);  GET_FREQ(&FREQUENCY);    \
        if(METALERP_CUDAMODE) {printf("----DEVICE ROUTINE MEASUREMENT----\n");}/*no trick-summing here due to the structure of the kernel loopers*/                            \
        heatUpPages(y##function##_DI_VEC, y##function##_DO_VEC, arr_len);  /*page-heating right before the measurement run*/\
        noDBG_qPerf( , function, y##function##_DI_VEC, y##function##_DO_VEC, arr_len) \
        totalT = (double)ELAPSED; /*total time is being measured here instead of aggregated since the whole loop finishes inside the function call*/ \
        free(y##function##_DI_VEC); free(y##function##_DO_VEC);\
        SLEEP(1); /*depending on the size of the array that just came, we might have really taxed the processor*/\
        perfSums = totalT;  \
        perfSums /= ((double)arr_len);                                     \
        printf("\n-------------------\nCall-> %s(MIXED RANDOM INPUT);\n\n(TOTAL TIME) ** %d iterations **:\n->%.6f (ms)\n->%.12f (s)\n\n(average SINGLE CALL exec time):\n->%.6f (ms)\n->%.4f (nanoSec)\n", #function, arr_len, totalT*1000.0, totalT, perfSums*1000.0, perfSums*1000000000.0); \
        trickSleep()} while(0);

    #define VEC_averagePerfDynamicInputNegative(arr_len, function)   \
        do {type* y##function##_DI_VEC##N = malloc(sizeof(type)*arr_len), *y##function##_DO_VEC##N = malloc(arr_len * sizeof(type));                      \
        type warmUpArrIN##function##DI##N[1000] = {0}, warmUpArrOUT##function##DI##N[1000] = {0}; \
        fillArr_RandomF(warmUpArrIN##function##DI##N, 1000, -1);                                          \
        fillArr_RandomF(y##function##_DI_VEC##N, arr_len, -1);       \
        function(y##function##_DI_VEC##N, warmUpArrOUT##function##DI##N, 1000); \
        if(METALERP_CUDAMODE) {printf("----DEVICE ROUTINE MEASUREMENT----\n");}perfSums = 0.0;  totalT = 0.0;   printf("\n**************************************************\n%s\n", #function);  GET_FREQ(&FREQUENCY);    \
        heatUpPages(y##function##_DI_VEC##N, y##function##_DO_VEC##N, arr_len);                        \
        noDBG_qPerf( , function, y##function##_DI_VEC##N, y##function##_DO_VEC##N, arr_len) \
        totalT = (double)ELAPSED;  \
        free(y##function##_DI_VEC##N); free(y##function##_DO_VEC##N);\
        SLEEP(1);\
        perfSums = totalT;  \
        perfSums /= ((double)arr_len);                                     \
        printf("\n-------------------\nCall-> %s(NEGATIVE RANDOM INPUT);\n\n(TOTAL TIME) ** %d iterations **:\n->%.6f (ms)\n->%.12f (s)\n\n(average SINGLE CALL exec time):\n->%.6f (ms)\n->%.4f (nanosec)\n", #function, arr_len, totalT*1000.0, totalT, perfSums*1000.0, perfSums*1000000000.0); \
        trickSleep()} while(0);

    #define VEC_averagePerfDynamicInputPositive(arr_len, function)   \
        do {type* y##function##_DI_VEC##P = malloc(sizeof(type)*arr_len), *y##function##_DO_VEC##P = malloc(arr_len * sizeof(type));                      \
        type warmUpArrIN##function##DI##P[1000] = {0}, warmUpArrOUT##function##DI##P[1000] = {0}; \
        fillArr_RandomF(warmUpArrIN##function##DI##P, 1000, 1);                                          \
        fillArr_RandomF(y##function##_DI_VEC##P, arr_len, 1);     \
        function(warmUpArrIN##function##DI##P, warmUpArrOUT##function##DI##P, 1000); \
        if(METALERP_CUDAMODE) {printf("----DEVICE ROUTINE MEASUREMENT----\n");}perfSums = 0.0;  totalT = 0.0;   printf("\n**************************************************\n%s\n", #function);  GET_FREQ(&FREQUENCY);    \
        heatUpPages(y##function##_DI_VEC##P, y##function##_DO_VEC##P, arr_len);                            \
        noDBG_qPerf( , function, y##function##_DI_VEC##P, y##function##_DO_VEC##P, arr_len) \
        totalT = (double)ELAPSED;  \
        free(y##function##_DI_VEC##P); free(y##function##_DO_VEC##P);\
        SLEEP(1);\
        perfSums = totalT;  \
        perfSums /= ((double)arr_len);                                     \
        printf("\n-------------------\nCall-> %s(POSITIVE RANDOM INPUT);\n\n(TOTAL TIME) ** %d iterations **:\n->%.6f (ms)\n->%.12f (s)\n\n(average SINGLE CALL exec time):\n->%.6f (ms)\n->%.4f (nanosec)\n", #function, arr_len, totalT*1000.0, totalT, perfSums*1000.0, perfSums*1000000000.0); \
        trickSleep()} while(0);



#endif

    
