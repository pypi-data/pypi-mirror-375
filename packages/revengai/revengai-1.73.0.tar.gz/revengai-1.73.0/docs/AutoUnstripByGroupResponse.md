# AutoUnstripByGroupResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**progress** | **int** | Progress of the auto-unstrip operation, represented as a percentage | [optional] [default to 0]
**status** | **str** |  | [optional] 
**total_time** | **int** |  | [optional] 
**matches_map** | **Dict[str, List[MatchedFunctionGroup]]** |  | [optional] 
**applied** | **bool** |  | [optional] 

## Example

```python
from revengai.models.auto_unstrip_by_group_response import AutoUnstripByGroupResponse

# TODO update the JSON string below
json = "{}"
# create an instance of AutoUnstripByGroupResponse from a JSON string
auto_unstrip_by_group_response_instance = AutoUnstripByGroupResponse.from_json(json)
# print the JSON string representation of the object
print(AutoUnstripByGroupResponse.to_json())

# convert the object into a dict
auto_unstrip_by_group_response_dict = auto_unstrip_by_group_response_instance.to_dict()
# create an instance of AutoUnstripByGroupResponse from a dict
auto_unstrip_by_group_response_from_dict = AutoUnstripByGroupResponse.from_dict(auto_unstrip_by_group_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


