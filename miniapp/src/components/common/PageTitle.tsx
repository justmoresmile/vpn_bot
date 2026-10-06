function PageTitle({

  title,

  subtitle,

}: {

  title: string

  subtitle: string

}) {



  return (



    <section className="page-title">



      <h1>

        {title}

      </h1>



      <p>

        {subtitle}

      </p>



    </section>

  )

}

export default PageTitle
