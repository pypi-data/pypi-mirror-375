# AutoUnstripRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**min_similarity** | **float** | Minimum similarity expected for a match, default is 0.9 | [optional] [default to 0.9]
**apply** | **bool** | Whether to apply the matched function names to the target binary, default is False | [optional] [default to False]

## Example

```python
from revengai.models.auto_unstrip_request import AutoUnstripRequest

# TODO update the JSON string below
json = "{}"
# create an instance of AutoUnstripRequest from a JSON string
auto_unstrip_request_instance = AutoUnstripRequest.from_json(json)
# print the JSON string representation of the object
print(AutoUnstripRequest.to_json())

# convert the object into a dict
auto_unstrip_request_dict = auto_unstrip_request_instance.to_dict()
# create an instance of AutoUnstripRequest from a dict
auto_unstrip_request_from_dict = AutoUnstripRequest.from_dict(auto_unstrip_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


