import pandas as pd
from collections import Counter
from itertools import combinations

class BasketAnalyzer:
    @staticmethod
    def analyze_associations(df: pd.DataFrame, min_support: int = 10, top_n: int = 10) -> pd.DataFrame:
        """
        计算商品两两连带率 (Pairwise Association)
        """
        # 1. 聚合订单商品
        # 只保留有 >1 件商品的订单
        basket = df.groupby('流水单号')['商品名称'].apply(list)
        basket = basket[basket.apply(len) > 1]
        
        if basket.empty:
            return pd.DataFrame()

        # 2. 统计共现 (Co-occurrence)
        pair_counts = Counter()
        item_counts = Counter()
        
        for items in basket:
            # 去重，同个订单买两个一样的只算一次关联
            unique_items = sorted(list(set(items)))
            
            for item in unique_items:
                item_counts[item] += 1
                
            for pair in combinations(unique_items, 2):
                pair_counts[pair] += 1
                
        # 3. 构建结果
        results = []
        for (item_a, item_b), count in pair_counts.most_common(top_n * 2): # 多取一点以便过滤
            if count < min_support:
                break
                
            support = count
            confidence_a_to_b = count / item_counts[item_a]
            confidence_b_to_a = count / item_counts[item_b]
            
            results.append({
                'item_a': item_a,
                'item_b': item_b,
                'co_occurrence': count,
                'conf_a_b': confidence_a_to_b,
                'conf_b_a': confidence_b_to_a
            })
            
        res_df = pd.DataFrame(results)
        if not res_df.empty:
            return res_df.head(top_n)
        return pd.DataFrame()
