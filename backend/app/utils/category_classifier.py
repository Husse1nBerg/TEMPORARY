"""
Category Classifier Utility
Path: backend/app/utils/category_classifier.py
"""

from typing import Dict, List, Optional
import re

class CategoryClassifier:
    """
    Classifies products into categories based on keywords.
    """

    def __init__(self):
        self.category_keywords: Dict[str, List[str]] = {
            "A": [
                "cucumber", "خيار", "tomato", "طماطم", "cherry tomato", 
                "طماطم كرزية", "capsicum mix", "pepper mix", "red capsicum", 
                "red pepper", "فلفل أحمر", "yellow capsicum", "yellow pepper", 
                "فلفل أصفر", "chili", "hot pepper", "فلفل حار", "arugula", 
                "rocket", "جرجير", "parsley", "بقدونس", "coriander", "cilantro", 
                "كزبرة", "mint", "نعناع", "tuscan kale", "lacinato kale", 
                "dinosaur kale", "basil", "italian basil", "ريحان"
            ],
            "B": [
                "colored cherry", "rainbow tomatoes", "green capsicum", 
                "green pepper", "فلفل أخضر", "italian arugula", "wild arugula", 
                "chives", "ثوم معمر", "curly kale", "kale", "batavia", 
                "batavia lettuce", "iceberg", "iceberg lettuce", "خس آيسبرغ", 
                "oak leaf", "oakleaf lettuce", "romaine", "romain lettuce", 
                "خس روماني"
            ]
        }

    def classify(self, product_name: str, description: Optional[str] = None) -> str:
        """
        Classify a product into a category based on its name and description.

        Args:
            product_name (str): The name of the product.
            description (Optional[str]): The product's description.

        Returns:
            str: The classified category ('A' or 'B'). Defaults to 'A'.
        """
        text_to_search = product_name.lower()
        if description:
            text_to_search += " " + description.lower()

        # Check for Category B keywords first
        for keyword in self.category_keywords["B"]:
            if re.search(r'\b' + re.escape(keyword) + r'\b', text_to_search):
                return "B"
        
        # Check for Category A keywords
        for keyword in self.category_keywords["A"]:
            if re.search(r'\b' + re.escape(keyword) + r'\b', text_to_search):
                return "A"
        
        # Default to Category A if no keywords are found
        return "A"