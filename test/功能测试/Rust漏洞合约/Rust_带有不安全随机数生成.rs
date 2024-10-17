#![cfg_attr(not(feature = "std"), no_std)]

use ink_lang as ink;

#[ink::contract]
mod briza {
    use ink_prelude::vec::Vec;
    //use ink_prelude::vec;
    /// Defines the storage of your contract.
    /// Add new fields to the below struct in order
    /// to add new static storage fields to your contract.
    #[ink(storage)]
    pub struct Briza {
        /// Stores a single `bool` value on the storage.
        value: u64,
    }

    impl Briza {
        #[ink(constructor)]
        pub fn new(va: u64) -> Self {
            Self { value: va}
        }

        /// A message that can be called on instantiated contracts.
        /// This one flips the value of the stored `bool` from `true`
        /// to `false` and vice versa.
        #[ink(message)]
        pub fn cal(&mut self) -> [u64;1000] {
            //let mut ans = Vec::<[u64;100]>::new();
            let mut ans = [0;1000];
            let vec_tmp1 = [1;1000];
            let vec_tmp2 = [1;1000];
            let vec_tmp3 = [1;1000];
            let vec_tmp4 = [1;1000];
            let vec_tmp5 = [6;1000];
            let length = 1000;
            
            for i in 0..length{
                let mut sum = 0;
                sum += vec_tmp1[i];
                sum += vec_tmp2[i];
                sum += vec_tmp3[i];
                sum += vec_tmp4[i];
                sum += vec_tmp5[i];
                ans[i] = sum / 5;
            }
            return ans;
            //self.value = !self.value;
        }


    }


    #[cfg(test)]
    mod tests {
        /// Imports all the definitions from the outer scope so we can use them here.
        use super::*;

        /// Imports `ink_lang` so we can use `#[ink::test]`.
        use ink_lang as ink;

        /// We test if the default constructor does its job.
        #[ink::test]
        fn default_works() {
            // let mut test = Briza::new();
            // let ans = test.cal();
            // assert_eq!(ans, vec![[3;10];338]);
        }

    }
}
