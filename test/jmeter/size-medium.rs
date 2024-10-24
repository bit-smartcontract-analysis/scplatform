#![cfg_attr(not(feature = "std"), no_std, no_main)]

// use ink_lang as ink;

#[ink::contract]
mod briza {
    //use ink_prelude::vec::Vec;
    use ink_prelude::vec::Vec;
    /// Defines the storage of your contract.
    /// Add new fields to the below struct in order
    /// to add new static storage fields to your contract.
    #[ink(storage)]
    pub struct Briza {
        /// Stores a single `bool` value on the storage.
        value: Vec<u64>,
        v2: Vec<u64>,
    }

    impl Briza {
        #[ink(constructor)]
        pub fn new(va: Vec<u64>, v: Vec<u64>) -> Self {
            Self { value: va, v2: v}
        }

        /// A message that can be called on instantiated contracts.
        /// This one flips the value of the stored `bool` from `true`
        /// to `false` and vice versa.
        #[ink(message)]
        pub fn cal(&mut self) -> Vec<u64> {
            let mut ans = Vec::<u64>::new();
            let mut tmp = 0;
            let length = self.value.len();
            for i in 0..length{
                let tmp1 = self.value.get(i).unwrap();
                let tmp2 = self.v2.get(i).unwrap();
                tmp = tmp1 + tmp2;
                tmp /=2;
                ans.push(tmp);
            }
            return ans;
            //self.value = !self.value;
        }


    }


}
