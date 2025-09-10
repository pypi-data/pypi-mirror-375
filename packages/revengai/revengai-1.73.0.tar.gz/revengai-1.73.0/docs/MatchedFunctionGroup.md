# MatchedFunctionGroup


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**function_group_name** | **str** | Name of the function group that contains the matched functions | 
**similarity** | **float** | Similarity score of the match | 

## Example

```python
from revengai.models.matched_function_group import MatchedFunctionGroup

# TODO update the JSON string below
json = "{}"
# create an instance of MatchedFunctionGroup from a JSON string
matched_function_group_instance = MatchedFunctionGroup.from_json(json)
# print the JSON string representation of the object
print(MatchedFunctionGroup.to_json())

# convert the object into a dict
matched_function_group_dict = matched_function_group_instance.to_dict()
# create an instance of MatchedFunctionGroup from a dict
matched_function_group_from_dict = MatchedFunctionGroup.from_dict(matched_function_group_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


