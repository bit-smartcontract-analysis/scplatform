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
    }
}
