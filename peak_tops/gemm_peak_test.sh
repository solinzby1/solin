  #!/bin/bash 
# Define the test items for different datetype 

datatypes=("fp16.yaml" "bf16.yaml" "fp64.yaml" "fp8.yaml" "fp32.yaml" "int8.yaml" "tf32.yaml") 

# Loop through each combination and run the command 
datatypes_length=${#datatypes[@]}
for ((i=0; i<datatypes_length;i++)); do
    file="${datatypes[$i]}"
    basename=$(echo "$file" | awk -F. '{print $1}')
    j=0
    max=7
    while [ $j -le $max ]
    do
        echo "$basename"
        echo "$j"
        if [ $i -lt 4 ]; then 
            cmd="ROCR_VISIBLE_DEVICES=$j HIP_FORCE_DEV_KERNARG=1 rocblas-bench --yaml ${datatypes[$i]}"
        else
            cmd="ROCR_VISIBLE_DEVICES=$j HIP_FORCE_DEV_KERNARG=1 hipblaslt-bench --yaml ${datatypes[$i]}"
        fi
    
        result=$(eval "$cmd" | tail -1)

        result_without_spaces=$(echo "$result" | tr -d ' ')
        substring_after_second_last_comma=$(echo "$result_without_spaces" | awk -F, '{print $(NF-1) "," $NF}')
        echo $substring_after_second_last_comma
        ((j++))
        done
done
