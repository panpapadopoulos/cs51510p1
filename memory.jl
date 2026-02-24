# ============================================================
# MEMORY DATABASE USING DOUBLY LINKED LIST
# Algorithms supported:
#    • Insertion Sort
#    • Bubble Sort
# ============================================================

using CSV
using DataFrames

# ============================================================
# DOUBLY LINKED LIST STRUCTURES
# ============================================================

mutable struct Node
    data::Dict{String,String}
    prev::Union{Node,Nothing}
    next::Union{Node,Nothing}
end


mutable struct DoublyLinkedList
    head::Union{Node,Nothing}
    tail::Union{Node,Nothing}
    size::Int
end


function create_list()
    DoublyLinkedList(nothing, nothing, 0)
end


function append!(list::DoublyLinkedList, data::Dict{String,String})

    new_node = Node(data, nothing, nothing)

    if list.head === nothing

        list.head = new_node
        list.tail = new_node

    else

        list.tail.next = new_node
        new_node.prev = list.tail
        list.tail = new_node

    end

    list.size += 1

end


# ============================================================
# LOAD CSV
# ============================================================

function load_csv_to_list!(filename::String, list::DoublyLinkedList)

    df = CSV.read(filename, DataFrame)

    headers = string.(names(df))

    for row in eachrow(df)

        dict = Dict{String,String}()

        for col in names(df)
            dict[string(col)] = string(row[col])
        end

        append!(list, dict)

    end

    return headers

end


# ============================================================
# COMPARISON FUNCTION
# ============================================================

function should_swap(v1::String, v2::String, order::String)

    order = uppercase(strip(order))

    try

        a = parse(Float64, strip(v1))
        b = parse(Float64, strip(v2))

        return order == "ASC" ? a > b : a < b

    catch

        return order == "ASC" ? v1 > v2 : v1 < v2

    end

end


# ============================================================
# INSERTION SORT
# ============================================================

function insertion_sort!(list::DoublyLinkedList,
                         column::String,
                         order::String)

    if list.head === nothing
        return
    end

    current = list.head.next

    while current !== nothing

        key = current.data

        move = current.prev

        while move !== nothing &&
              should_swap(move.data[column], key[column], order)

            move.next.data = move.data

            move = move.prev
        end

        if move === nothing
            list.head.data = key
        else
            move.next.data = key
        end

        current = current.next

    end

end


# ============================================================
# BUBBLE SORT
# ============================================================

function bubble_sort!(list::DoublyLinkedList,
                      column::String,
                      order::String)

    if list.head === nothing
        return
    end

    swapped = true

    while swapped

        swapped = false

        current = list.head

        while current.next !== nothing

            if should_swap(current.data[column],
                           current.next.data[column],
                           order)

                # swap data
                current.data,
                current.next.data =
                current.next.data,
                current.data

                swapped = true

            end

            current = current.next

        end

    end

end


# ============================================================
# RECURSIVE EXPORT
# ============================================================

function export_recursive(node::Union{Node,Nothing},
                          io,
                          columns)

    if node === nothing
        return
    end

    row = [get(node.data, col, "") for col in columns]

    println(io, join(row, ","))

    export_recursive(node.next, io, columns)

end


function export_to_csv(list::DoublyLinkedList,
                       filename::String,
                       columns)

    open(filename, "w") do io

        println(io, join(columns, ","))

        export_recursive(list.head, io, columns)

    end

end


# ============================================================
# SORT SELECTOR
# ============================================================

function sort_by_algorithm!(list,
                            algorithm,
                            column,
                            order)

    algorithm = lowercase(strip(algorithm))

    if algorithm == "insertion_sort"

        insertion_sort!(list, column, order)

    elseif algorithm == "bubble_sort"

        bubble_sort!(list, column, order)

    else

        error("Supported algorithms: insertion_sort, bubble_sort")

    end

end


# ============================================================
# MAIN FUNCTION
# ============================================================

function main()

    input_file = "student-data.csv"
    output_file = "output.csv"

    # CHANGE THIS QUERY AS NEEDED
    algorithm = "insertion_sort"
    # algorithm = "bubble_sort"

    column = "age"
    order = "ASC"

    list = create_list()

    headers = load_csv_to_list!(input_file, list)

    println("Loaded ", list.size, " records")

    sort_by_algorithm!(list,
                       algorithm,
                       column,
                       order)

    export_to_csv(list,
                  output_file,
                  headers)

    println("Sorted using ", algorithm)
    println("Exported to output.csv")

end


main()