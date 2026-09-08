import streamlit as st


def safe_chai_bill(cups, price_per_cup):
    """Calculate chai bill safely.

    - `cups` should represent a whole number (>= 1).
    - `price_per_cup` should be a number (float).
    Raises ValueError for invalid input.
    Returns the total bill as a float.
    """
    try:
        # allow inputs like '2' or '2.0' but reject '2.5'
        cups_float = float(cups)
        if not cups_float.is_integer():
            raise ValueError("Cups must be a whole number.")
        cups_int = int(cups_float)

        price = float(price_per_cup)

        if cups_int < 1:
            raise ValueError("Cups must be at least 1.")

        total = cups_int * price
        return total

    except ValueError:
        # re-raise to let the caller handle display
        raise


def main():
    st.title("Chai Bill Calculator")
    st.write("Enter how many cups of chai and the price per cup.")

    cups = st.text_input("Cups", "1")
    price = st.text_input("Price per cup", "2.50")

    if st.button("Calculate"):
        try:
            total = safe_chai_bill(cups, price)
        except ValueError as e:
            st.error(f"Input error: {e}")
        else:
            st.success(f"Total chai bill: {total:.2f}")


if __name__ == "__main__":
    main()
