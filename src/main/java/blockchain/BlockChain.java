package com.megvii.blockchain;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import com.megvii.Util;
import com.megvii.blockchain.entity.Block;
import com.megvii.blockchain.entity.BlockHead;
import com.megvii.blockchain.entity.Transaction;

public class BlockChain
{
    private static final String LOCALHOST_ADDR = "127.0.0.1:8080";
    private static final String BLOCK_CHAIN_VERSION = "0x01";
    private static final String Key_BASE = "KeyBase";

    private ArrayList<Block> mBlockChain;
    private ArrayList<Transaction> mTransactions;

    private int mTarget;

    private static volatile BlockChain mInstance;

    private BlockChain()
    {
        mBlockChain = new ArrayList<>();
        mTransactions = new ArrayList<>();
        mTarget = 0;
    }

    public static BlockChain getInstance()
    {
        if (mInstance == null)
        {
            synchronized (BlockChain.class)
            {
                if (mInstance == null)
                    mInstance = new BlockChain();
            }
        }
        return mInstance;
    }

    private Block getLastBlock()
    {
        return mBlockChain.size() > 0 ? mBlockChain.get(mBlockChain.size() - 1) : null;
    }

    /**
     * Initialize blockchain
     */
    void init(boolean rule)
    {
        System.out.println("BlockChain init!\nReady to create the ROOT block!");
        Block mRootBlock = newBlock(Util.MD5(LOCALHOST_ADDR));
        int nonce = 0;
        if (rule)
        {
            while (!Util.isPoWNonce(mRootBlock.getHead().toPowString(), nonce))
                nonce++;
        }
        else
            nonce = Util.getRandomNonce();
        ensureBlock(mRootBlock, nonce);
    }

    /**
     * pseudocode 
     * Run sha256 hashes twice on the block header
     * if the result < target difficulty level specified in the block header
     * success
     */
    @SuppressWarnings("unused")
    private Block getNextBlockByPOW()
    {
        Block block = newBlock(Util.MD5(LOCALHOST_ADDR));
        for (int nonce = 0; nonce < Math.pow(2, 32); ++nonce)
        {

            String headStr = block.getHead().toPowString() + nonce;
            Integer sha256 = new Integer(Util.SHA256(Util.SHA256(headStr)));
            // calculated sha256 value <=  target value 
            // indicates: a new block was found
            if (sha256.compareTo(mTarget) <= 0)
            {
                ensureBlock(block, nonce);
                break;
            }
        }
        return block;
    }

    /**
     * Define POW
     * Find a natural number "nonce" 
     * that makes the first 6 bits of 
     * md5(version + previous_block_hash + merkle_root + time + target_bits + nonce) are 0
     */
    @SuppressWarnings("all")
    public Block getNextBlockByPOW(String host, int port)
    {
        int nonce = 0;
        Block block = newBlock(Util.MD5(host + port));
        while (!Util.isPoWNonce(block.getHead().toPowString(), nonce))
            nonce++;
        ensureBlock(block, nonce);
        return block;
    }

    /**
     * Simulation
     */
    public void getNextBlock(String host, int port)
    {
        int nonce = Util.getRandomNonce();
        System.out.println(String.format(Locale.CHINESE, "Nonce %d has been found! MD5 : %s", nonce, Util.MD5(nonce + "")));
        Block block = newBlock(Util.MD5(host + port));
        ensureBlock(block, nonce);
    }

    public void newTransaction(String from, String to, int amount)
    {
        Transaction transaction = new Transaction(from, to, amount);
        mTransactions.add(transaction);
        System.out.println(String.format("Create a transaction: %s", transaction.toString()));
    }

    /**
     * Create a block entity via POW
     * @param toAddr The address to which the block belongs is a string of MD5
     */
    private Block newBlock(String toAddr)
    {
        // Block Rewards 
        // Transaction History
        newTransaction(Key_BASE, toAddr, 10);
        List<Transaction> transactions = new ArrayList<>(mTransactions);
        Block last = getLastBlock();
        // Initialize BlockHead
        BlockHead head = new BlockHead(BLOCK_CHAIN_VERSION, last != null ? last.toString() : "", Util.getMerkleRoot(transactions), System.currentTimeMillis() + "", mTarget);
        return new Block(last != null ? last.getIndex() + 1 : 0, head, transactions);
    }

    /**
     * Chain-in the block
     */
    private void ensureBlock(Block block, int nonce)
    {
        block.getHead().setNonce(nonce);
        // Chain-in the block
        mBlockChain.add(block);
        // Update Target
        mTarget++;
        // Clear Transactions
        mTransactions.removeAll(block.getTransactions());
        System.out.println(String.format(Locale.CHINESE, "Block #%d has been added!\r\nHash: %s", block.getIndex(), block.toString()));
        pushBlockChainToAll();
    }

    private void pushBlockChainToAll()
    {
        // TODO pushes the newly generated blocks to all nodes
    }
}
