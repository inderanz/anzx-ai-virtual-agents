"use client"

import { motion } from "framer-motion"
import { ArrowRight, Play } from "lucide-react"
import { cta } from "@/content/site"
import { Button } from "@/components/ui/button"

export function CTA() {
  return (
    <section className="py-24 sm:py-32 bg-primary">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          viewport={{ once: true }}
          className="mx-auto max-w-2xl text-center"
        >
          <h2 className="text-3xl font-bold tracking-tight text-primary-foreground sm:text-4xl">
            {cta.title}
          </h2>
          <p className="mt-6 text-lg leading-8 text-primary-foreground/90">
            {cta.description}
          </p>
          <div className="mt-10 flex items-center justify-center gap-x-6">
            <Button size="lg" variant="secondary" asChild>
              <a href={cta.cta.primary.href}>
                {cta.cta.primary.text}
                <ArrowRight className="ml-2 h-4 w-4" />
              </a>
            </Button>
            <Button size="lg" variant="outline" className="border-primary-foreground text-primary-foreground hover:bg-primary-foreground hover:text-primary" asChild>
              <a href={cta.cta.secondary.href} className="flex items-center">
                <Play className="mr-2 h-4 w-4" />
                {cta.cta.secondary.text}
              </a>
            </Button>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
