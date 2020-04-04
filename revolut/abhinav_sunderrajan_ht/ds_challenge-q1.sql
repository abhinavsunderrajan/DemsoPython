select (mean_trans_week_later-mean_trans_prior_week) as difference,
week_later_avg.country,week_later_avg.age_group from

(
    select avg(num_transactions_week_prior) mean_trans_prior_week, country,age_group from(
    select count(*) as num_transactions_week_prior,user_id, country,age_group   from
    (
        select notifs.user_id, notifs.age_group, notifs.country,notifs.notif_date,
        transactions.created_date as transaction_date
        from transactions
        inner join
        (select distinct (2020- birth_year)/10 as  age_group, country, notifications.user_id as user_id,
        notifications.created_date as notif_date from users
        inner join notifications on users.user_id= notifications.user_id) as notifs
        on transactions.user_id = notifs.user_id
    ) as temp_table
    where extract(epoch from transaction_date - notif_date)<0 and
    extract(epoch from transaction_date - notif_date) > -(7*24*3600)
    group by user_id, country,age_group)
    as trans_week_prior group by country,age_group
) as week_prior_avg

inner join (
    select avg(num_transactions_week_later) mean_trans_week_later, country,age_group from(
    select count(*) as num_transactions_week_later,user_id, country,age_group   from
    (
        select notifs.user_id, notifs.age_group, notifs.country,notifs.notif_date,
        transactions.created_date as transaction_date
        from transactions
        inner join
        (select distinct (2020- birth_year)/10 as  age_group, country, notifications.user_id as user_id,
        notifications.created_date as notif_date from users
        inner join notifications on users.user_id= notifications.user_id) as notifs
        on transactions.user_id = notifs.user_id
    ) as temp_table
    where extract(epoch from transaction_date - notif_date)>0 and
    extract(epoch from transaction_date - notif_date) < (7*24*3600)
    group by user_id, country,age_group)
    as trans_week_later group by country,age_group
) as week_later_avg

on  week_later_avg.country= week_prior_avg.country AND week_later_avg.age_group=week_prior_avg.age_group
