/* tslint:disable */
/* eslint-disable */
/**
 * FastAPI
 * No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)
 *
 * The version of the OpenAPI document: 0.1.0
 *
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 */

import { exists, mapValues } from '../runtime';
import type { Severity } from './Severity';
import { SeverityFromJSON, SeverityFromJSONTyped, SeverityToJSON } from './Severity';

/**
 * A Problem affecting multiple rows of the dataset
 * @export
 * @interface DataIssue
 */
export interface DataIssue {
    /**
     *
     * @type {Severity}
     * @memberof DataIssue
     */
    severity: Severity;
    /**
     *
     * @type {string}
     * @memberof DataIssue
     */
    description: string;
    /**
     *
     * @type {Array<number>}
     * @memberof DataIssue
     */
    rows: Array<number>;
}

/**
 * Check if a given object implements the DataIssue interface.
 */
export function instanceOfDataIssue(value: object): boolean {
    let isInstance = true;
    isInstance = isInstance && 'severity' in value;
    isInstance = isInstance && 'description' in value;
    isInstance = isInstance && 'rows' in value;

    return isInstance;
}

export function DataIssueFromJSON(json: any): DataIssue {
    return DataIssueFromJSONTyped(json, false);
}

export function DataIssueFromJSONTyped(
    json: any,
    ignoreDiscriminator: boolean
): DataIssue {
    if (json === undefined || json === null) {
        return json;
    }
    return {
        severity: SeverityFromJSON(json['severity']),
        description: json['description'],
        rows: json['rows'],
    };
}

export function DataIssueToJSON(value?: DataIssue | null): any {
    if (value === undefined) {
        return undefined;
    }
    if (value === null) {
        return null;
    }
    return {
        severity: SeverityToJSON(value.severity),
        description: value.description,
        rows: value.rows,
    };
}
