# UnstripRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**min_similarity** | **float** | Minimum similarity expected for a match, default is 0.9 | [optional] [default to 0.9]
**limit** | **int** | Maximum number of matches to return, default is 1, maximum is 10 | [optional] [default to 1]
**apply** | **bool** | Whether to apply the matched function names to the target binary, default is False | [optional] [default to False]

## Example

```python
from revengai.models.unstrip_request import UnstripRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UnstripRequest from a JSON string
unstrip_request_instance = UnstripRequest.from_json(json)
# print the JSON string representation of the object
print(UnstripRequest.to_json())

# convert the object into a dict
unstrip_request_dict = unstrip_request_instance.to_dict()
# create an instance of UnstripRequest from a dict
unstrip_request_from_dict = UnstripRequest.from_dict(unstrip_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


