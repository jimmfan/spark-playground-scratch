def overwrite_by_dates(
    session,
    df_new,
    table_name: str,
    date_col: str,
    date_values,  # iterable of dates/strings
):
    target = session.table(table_name)

    # 1. Delete old rows for these dates
    (
        target
        .filter(F.col(date_col).isin([F.lit(d) for d in date_values]))
        .delete()
    )

    # 2. Append the replacement data
    df_new.write.mode("append").save_as_table(table_name)
